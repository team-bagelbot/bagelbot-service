from google.cloud import storage
from app_logger import AppLogger

class StorageManager(AppLogger):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)
        AppLogger.__init__(self, f'{self.bucket_name}-storage-manager-logger')
        self.log_text(f'Initialized logger: {bucket_name}-storage-manager-logger PROJECT_ID: {bucket_name}')

    def read_blob(self, blob_name):
        """Write and read a blob from GCS using file-like IO"""
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your new GCS object
        # blob_name = "storage-object-name"

        blob = self.bucket.blob(blob_name)

        # Mode can be specified as wb/rb for bytes mode.
        # See: https://docs.python.org/3/library/io.html
        #with blob.open("w") as f:
            #f.write("Hello world")

        with blob.open("r") as f:
            self.log_text(f"read from bucket: {self.bucket_name} file: {blob_name}")
            return f.read()
    
    def append_blob(self, data):
        """Append data to an existing blob."""
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your GCS object
        # blob_name = "storage-object-name"

        # get blob list and total number of blobs
        blob_list = self._list_blobs()
        total_blobs = len(blob_list)

        # create a new blob name
        source_file_name = self._get_new_blob_name(total_blobs)

        # save the new question to disk
        try:
            with open(source_file_name, 'w') as f:
                f.write(data.strip() + '\n')
        except Exception as e:
            self.log_text(f'error writing {source_file_name} to disk: {e}')
            raise e

        # upload the new question to a new blob in GCS
        blob = self.bucket.blob(source_file_name)

        try:
            blob.upload_from_filename(source_file_name)
        except Exception as e:
            self.log_text(f'error uploading {source_file_name} to {source_file_name} in bucket {self.bucket_name}: {e}')
            raise e
        else:
            self.log_text(
                f"File {source_file_name} uploaded to {source_file_name} in bucket {self.bucket_name}."
            )
            pass

        blob_list = self._list_blobs()

        # compose the new blob with the existing blobs
        try:
            self._compose(blob_list, 'empty_responses.txt')
        except Exception as e:
            self.log_text(f'error composing empty_responses.txt with {source_file_name}: {e}')
            raise e
        else:
            self.log_text(f"empty_responses.txt composed with {source_file_name}")
            pass
        
        # delete the new blob
        blob = self.bucket.blob(source_file_name)
        try:
            blob.delete()
        except Exception as e:
            self.log_text(f'error deleting {source_file_name}: {e}')
            raise e
        else:
            self.log_text(f"successfully deleted {source_file_name}")
            pass
    

    def _list_blobs(self) -> list:
        """Lists all the blobs in the bucket."""

        blob_list = []

        # Note: Client.list_blobs requires at least package version 1.17.0.
        try:
            blob_list = list(self.storage_client.list_blobs(self.bucket_name, prefix='empty_responses'))
        except Exception as e:
            self.log_text(f'error listing blobs in bucket: {self.bucket_name}: {e}')
            raise e
        return blob_list

    def _compose(self, source_blob_names, destination_blob_name):
        """Compose multiple objects into one object."""
        # source_blob_names = ["object1", "object2", "object3"]
        # destination_blob_name = "object-composed"

        blob = self.bucket.blob(destination_blob_name)
        blob.compose(source_blob_names)

    def _get_new_blob_name(self, total_blobs) -> str:
        return f'empty_responses{total_blobs + 1}.txt'

