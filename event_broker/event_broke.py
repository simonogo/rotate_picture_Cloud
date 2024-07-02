import argparse
import json
import time
import os
from google.cloud import pubsub_v1, storage
import requests

api_url =""

def download(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    return blob.metadata["rotation"]

# Based on open code: https://github.com/googleapis/python-storage/blob/main/samples/snippets/notification_polling.py
def api_request(url, initial_file_path, roated_file_path, rotation):
    with open(initial_file_path, 'rb') as file:
        response = requests.post(url + f'/rotate/{rotation}', data=file, headers={'Content-Type': 'image/png'})
    
    if response.status_code == 200:
        with open(roated_file_path, 'wb') as out_file:
            out_file.write(response.content)
        print("Rotated picture saved")

def summarize(message):
    data = message.data.decode("utf-8")
    attributes = message.attributes

    event_type = attributes["eventType"]
    bucket_id = attributes["bucketId"]
    object_id = attributes["objectId"]
    generation = attributes["objectGeneration"]
    description = (
        "\tEvent type: {event_type}\n"
        "\tBucket ID: {bucket_id}\n"
        "\tObject ID: {object_id}\n"
        "\tGeneration: {generation}\n"
    ).format(
        event_type=event_type,
        bucket_id=bucket_id,
        object_id=object_id,
        generation=generation,
    )

    if "overwroteGeneration" in attributes:
        description += f"\tOverwrote generation: {attributes['overwroteGeneration']}\n"
    if "overwrittenByGeneration" in attributes:
        description += f"\tOverwritten by generation: {attributes['overwrittenByGeneration']}\n"

    payload_format = attributes["payloadFormat"]
    if payload_format == "JSON_API_V1":
        object_metadata = json.loads(data)
        size = object_metadata["size"]
        content_type = object_metadata["contentType"]
        metageneration = object_metadata["metageneration"]
        description += (
            "\tContent type: {content_type}\n"
            "\tSize: {object_size}\n"
            "\tMetageneration: {metageneration}\n"
        ).format(
            content_type=content_type,
            object_size=size,
            metageneration=metageneration,
        )

    if event_type == "OBJECT_FINALIZE":
        initial_picture_save_path = os.getenv("HOME") + f'/workspace/sending_picture/event_broker/initial_picture/picture-{generation}.png'
        rotated_picture_save_path = os.getenv("HOME") + f'/workspace/sending_picture/event_broker/rotated_picture/rotated_picture-{generation}.png'
        rotation=download(bucket_id, object_id, initial_picture_save_path )
        print("DOWNLOADED")
        api_request(api_url,  initial_picture_save_path, rotated_picture_save_path, rotation)
    return description


def poll_notifications(project, subscription_name):
    """Polls a Cloud Pub/Sub subscription for new GCS events for display."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project, subscription_name
    )

    def callback(message):
        print(f"Received message:\n{summarize(message)}")
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    # The subscriber is non-blocking, so we must keep the main thread from
    # exiting to allow it to process messages in the background.
    print(f"Listening for messages on {subscription_path}")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project", help="The ID of the project that owns the subscription"
    )
    parser.add_argument(
        "subscription", help="The ID of the Pub/Sub subscription"
    )
    parser.add_argument(
        '-a', '--api', help='Opis opcjonalnego argumentu')
    args = parser.parse_args()

    if args.api is not None:
        api_url=args.api
    poll_notifications(args.project, args.subscription)