import flask
import logging
import os
# Imports the Google Cloud client library
from google.cloud import storage

# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = "mysql_to_mongo_export"

# The name of the object in bucket
source_blob_name = "demo_images/demo1.jpg"

# The name of the downloaded object
destination_file_name = "demo1.jpg"

# Creates the new bucket
# bucket = storage_client.create_bucket(bucket_name)

# print(f"Bucket {bucket.name} created.")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    # contents = blob.download_as_string()
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    # main()
    download_blob(bucket_name, source_blob_name, destination_file_name)
