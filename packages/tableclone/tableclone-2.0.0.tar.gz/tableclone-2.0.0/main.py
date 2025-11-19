import logging
import json
import base64
from flask import make_response, jsonify
from werkzeug.exceptions import BadRequest
from tableclone.platforms.factory import table_factory, platform_factory
from tableclone.tasking.v1_implementation import BubbleTask
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)

DEV = False


def process_task(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    if DEV:
        with open("test.json") as f:
            j = json.load(f)
            logger.debug("Input data : %s" % (j))
    else:
        j = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
        logger.debug("Input data : %s" % (j))

    BubbleTask(j, log_level=logging.INFO).process(export_csv=False)


if __name__ == "__main__":
    DEV = True  # Switch to false once deployed
    process_task("event", "context")


def object_info(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    try:
        request_json = request.get_json()
        logger.info("Request received, JSON %s" % (request_json))

        table = table_factory(
            request_json["table"]["platform"],
            "",
            {
                "platform_root_path": request_json["table"]["platform_root_path"],
                "secret_string": request_json["table"]["credential_token"],
            },
            request_json["table"]["api_identifier"],
            column_mask=None,
            check=False,
        )

        response_json = table.object_info()

        return make_response(json.dumps(response_json), 200)

    except Exception as e:
        logging.exception("Exception occured")
        return make_response("Bad Request", 400)


def list(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    try:
        request_json = request.get_json()
        logger.info("Request received, JSON %s" % (request_json))

        platform = platform_factory(
            request_json["table"]["platform"],
            request_json["table"]["platform_root_path"],
            request_json["table"]["credential_token"],
        )

        response_json = platform.list(request_json["level"], request_json["parent"])

        return make_response(json.dumps(response_json), 200)

    except Exception as e:
        logging.exception("Exception occured")
        return make_response(
            "Bad Request: " + e.__class__.__name__ + " - " + str(e), 400
        )


def publish_pub_sub(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    try:
        request_data = request.get_data(as_text=True)
        request_json = request.get_json()

        logger.info("Request received, JSON %s" % (request_json))

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path("bubble-sync", "taskv2")
        future = publisher.publish(
            topic_path,
            json.dumps(request_json).encode(),
            origin="publishPubSub",
        )
        response = {"message": "PubSub message sent", "request": request_json}
        return make_response(jsonify(response), 200)

    except BadRequest:
        response = {"message": "Bad Request: Malformed JSON", "request": request_data}
        return make_response(jsonify(response), 400)

    except Exception as e:
        logging.exception("Exception occured")
        response = {
            "message": "Bad Request: " + e.__class__.__name__ + " - " + str(e),
            "request": request_json,
        }
        return make_response(jsonify(response), 400)
