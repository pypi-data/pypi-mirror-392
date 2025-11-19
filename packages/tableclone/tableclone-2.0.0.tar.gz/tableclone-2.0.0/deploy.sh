# tableclonev2-process
gcloud functions deploy tableclonev2-process --region=europe-west1 --runtime=python310 --source=. \
    --entry-point=process_task --project=bubble-sync --trigger-topic=taskv2 

# tableclonev2-list 
gcloud functions deploy tableclonev2-list --region=europe-west1 --runtime=python310 --source=. \
    --entry-point=list --project=bubble-sync --trigger-http

# tableclonev2-object_info 
gcloud functions deploy tableclonev2-object_info  --region=europe-west1 --runtime=python310 --source=. \
    --entry-point=object_info --project=bubble-sync --trigger-http

# tableclonev2-publish_pub_sub  
gcloud functions deploy tableclonev2-publish_pub_sub --region=europe-west1 --runtime=python310 --source=. \
    --entry-point=publish_pub_sub --project=bubble-sync --trigger-http