import os
import sys
from google.cloud import storage
from datetime import datetime

picture= sys.argv[1]
rotate= sys.argv[2]


def upload_image_to_gcs(bucket_name, source_file_name, destination_blob_name, metadata):
    """Uploads a file to the bucket with metadata."""
    
    # Create client
    storage_client = storage.Client()

    # Reference to bucket 
    bucket = storage_client.bucket(bucket_name)

    # Create blob
    blob = bucket.blob(destination_blob_name)

    # MAETADATA
    blob.metadata = metadata

    # Upload to Gcs
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name} with metadata {metadata}.")

# Variables 
bucket_name = os.getenv('BUCKET_NAME') 
home = os.getenv('HOME')
source_file_name = f'{home}/workspace/sending_picture/{picture}'
destination_blob_name = '/picture/picture.png'

metadata = {
    'description': 'new_picture',
    'rotation' : rotate,
    'author': 'Szymon'
}

if __name__ == "__main__":
    # Exec function
    upload_image_to_gcs(bucket_name, source_file_name, destination_blob_name, metadata)