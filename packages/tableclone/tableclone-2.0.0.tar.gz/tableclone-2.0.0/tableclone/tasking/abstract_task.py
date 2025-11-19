import logging
from abc import ABC, abstractmethod
from typing import Any

import requests
from requests.exceptions import HTTPError

from ..platforms.abstracts import FileContainer, PlatformObject
from ..utils import OptionSet, OptionValues, get_logger, setup_logging


class TaskInterface(ABC):
    OPTION_SET = OptionSet([])  # Empty option set
    LOGGER = logging.getLogger(__name__)

    def __init__(self, config: dict, log_level: int = logging.INFO):
        self.config = self._validate_config(config)
        setup_logging()
        self.logger = get_logger(self.__class__.__name__)

        self._setup()

    def log(self, message, level="info"):
        getattr(self.logger, level)(message)

    @property
    @abstractmethod
    def source(self) -> PlatformObject:
        """The source object."""
        pass

    @property
    @abstractmethod
    def destination(self) -> PlatformObject:
        """The destination object."""
        pass

    @abstractmethod
    def _setup(self):
        """Instanciate source and destination as objects"""
        pass

    @abstractmethod
    def _validate_config(self, config: dict) -> dict:
        self.options_values = OptionValues(
            self.OPTION_SET, config.get("options", {})
        )  # this validates the option values
        return config

    def error_callback(self, error_message):
        self.log(error_message, "warning")
        self._error_callback_impl(error_message)

    @abstractmethod
    def _error_callback_impl(self, error_message):
        pass

    def success_callback(self, *args, **kwargs):
        self.log("Processing success callback", "info")
        self._success_callback_impl(*args, **kwargs)
        self.log("Task Completed", "info")

    @abstractmethod
    def _success_callback_impl(self, *args, **kwargs):
        pass

    @staticmethod
    def with_callbacks_decorator(task_function):
        def wrapper(instance: "TaskInterface", *args, **kwargs):
            try:
                result = task_function(instance, *args, **kwargs)
                instance.success_callback(**result)
                return result
            except HTTPError as e:
                instance.error_callback(
                    e.__class__.__name__ + " - " + str(e) + "\n" + e.response.text
                )
                raise e
            except Exception as e:
                instance.error_callback(e.__class__.__name__ + " - " + str(e))
                raise e

        return wrapper

    @abstractmethod
    def _process_impl(self, *args, **kargs) -> dict[str, Any]:
        """Results will be passed as *args, **kwargs to success_callback"""
        pass

    @with_callbacks_decorator
    def process(self, *args, **kargs):
        return self._process_impl(*args, **kargs)


class TaskInterfaceWithWebHookCallbacks(TaskInterface):
    """
    Task config should calbacks with a url and params

    example
    {
    ...
        "success_callback": [
            {
                "url": "xxx",
                "params": {},
                "headers": {}"
            }
        ],
        "error_callback": [
            {
                "url": "xxx",
                "params": {},
                "headers": {}"
            }
        ],
    }
    """

    def SuccessWebHookCallback(self, url: str, params: dict = {}, headers: dict = {}):
        # If destination is a FileContainer, we will send the file to the callback URL
        if isinstance(self.destination, FileContainer):
            file_path = self.destination.platform.platform_root_path
            with open(
                file_path,
                "rb",
            ) as f:
                files_ = {
                    "file": (
                        file_path,
                        f,
                        self.destination.MIME_TYPE,
                    )
                }
                response = requests.post(
                    url,
                    # We send task_id and post_params
                    params={
                        **params,
                        **{"task_id": self.config.get("task_id")},
                        "status": "success",
                    },
                    headers=headers,
                    files=files_,
                )
                response.raise_for_status()
        # Else we just send the params
        else:
            response = requests.post(
                url,
                # We send task_id and post_params
                params={
                    **params,
                    **{"task_id": self.config.get("task_id")},
                    "status": "success",
                },
                headers=headers,
            )
            response.raise_for_status()
        pass

    def ErrorWebHookCallback(
        self, error_message: str, url: str, params: dict = {}, headers: dict = {}
    ):
        # we callback with task_id and error message
        requests.post(
            url,
            params={
                **params,
                **{
                    "task_id": self.config.get("task_id"),
                    "status": "error",
                    "error": error_message,
                },
            },
            headers=headers,
        )

    def _success_callback_impl(self, *args, **kwargs):
        for callback in self.config["success_callback"]:
            self.SuccessWebHookCallback(**callback)

    def _error_callback_impl(self, error_message):
        for callback in self.config["error_callback"]:
            self.ErrorWebHookCallback(error_message, **callback)
