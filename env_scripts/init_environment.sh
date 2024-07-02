#!/bin/bash

# Export env Variablees
number=$RANDOM
export PROJECT_NAME="mystudy-419512"
export BUCKET_NAME="was-szy-bucket-$number"
export BUCKET_ADDR="gs://$BUCKET_NAME"
export BUCKET_LOCATION="NORTHAMERICA-NORTHEAST1"
export TOPIC_NAME="NEW_PICTURE-$number"
export NOTIF_NAME="notify-storage-changes-$number"
export API_REGION="northamerica-northeast1"
export API_NAME="python-rest-api"

# Create new bucket
gcloud storage buckets create --location=$BUCKET_LOCATION $BUCKET_ADDR

# Create topic
gcloud pubsub topics create $TOPIC_NAME

# Create notification
gcloud storage buckets notifications create $BUCKET_ADDR --topic=$TOPIC_NAME

# Create Subsciption
gcloud pubsub subscriptions create $NOTIF_NAME --topic=$TOPIC_NAME

# Deply python-rest-api in Cloud RUN
gcloud run deploy $API_NAME --region=$API_REGION --allow-unauthenticated --source  /home/my_user/workspace/rotate_script  --quiet --platform managed

# Export API_ADDR
export API_ADDR=$(gcloud run services describe $API_NAME  --platform managed --format 'value(status.url)' --region=$API_REGION)

# Run Event Broker
source /home/$USER/workspace/sending_picture/venv/bin/activate
nohup python3 /home/$USER/workspace/sending_picture/event_broker/event_broke.py $PROJECT_NAME $NOTIF_NAME --api $API_ADDR &
echo "Event Broker is running ..."

