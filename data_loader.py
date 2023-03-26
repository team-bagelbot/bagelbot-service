import time
from storage_manager import StorageManager
from llama_index import GPTSimpleVectorIndex

class DataLoader(StorageManager):
    def __init__(self, bucket_name, hash_file, index_local_file, questions_local_file) -> None:
        self.bucket_name = bucket_name
        self.hash_file = hash_file
        self.index_local_file = index_local_file
        self.questions_local_file = questions_local_file
        StorageManager.__init__(self, bucket_name)
        self.last_sha = None
        self.index = None
        self.last_loaded_index_time = None
        self.questions = None

    def load_index(self) -> GPTSimpleVectorIndex:
        sha = self._pull_sha()
        if sha != self.last_sha:
            self._pull_index()
            self._load_index_from_disk()
            self.last_sha = sha
        return self.index
    
    def load_questions(self) -> str:
        self._pull_questions()
        return self.questions
  
    def _pull_sha(self) -> str:
        try:
            sha = self.read_blob(self.hash_file)
        except Exception as e:
            print(f'Error reading index file: {e}')
            return 'error'
        else:
            return sha

    def _pull_index(self) -> None:
        try:
            index_data = self.read_blob(self.index_local_file)
        except Exception as e:
            print(f"Error reading index file: {e}")
            return
        else:
            self._write_index(index_data)

    def _write_index(self, index_data):
        try:
            f = open(self.index_local_file, 'w')
            f.write(index_data)
            f.close()
        except Exception as e:
            print(f"Error writing index file: {e}")

    def _load_index_from_disk(self):
        self.index = GPTSimpleVectorIndex.load_from_disk(self.index_local_file)
        self.last_loaded_index_time = time.time()

    def _pull_questions(self) -> None:
        try:
            self.questions = self.read_blob(self.questions_local_file)
        except Exception as e:
            print(f"Error reading questions file: {e}")
            return 
