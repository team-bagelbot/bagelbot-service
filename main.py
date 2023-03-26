import os
import time

PROJECT_ID = os.environ['PROJECT_ID']
MAX_SECS_TO_LOAD_INDEX = 1800

from app_logger import AppLogger
logger_name = f'{PROJECT_ID}-service-logger'
logger = AppLogger(logger_name)
logger.log_text(f'MAX_SECS_TO_LOAD_INDEX: {MAX_SECS_TO_LOAD_INDEX}')
logger.log_text(f'Initialized logger: {logger_name} PROJECT_ID: {PROJECT_ID}')

from secrets_accessor import access_secret_version

OPENAI_API_KEY = access_secret_version(PROJECT_ID,'OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
logger.log_text(f'Retrieved OPENAI_API_KEY for PROJECT_ID: {PROJECT_ID}')

INDEX_VECTOR_LOCAL_FILE = 'index_vector.json'
QUESTIONS_FILE = 'questions.txt'
HASH_FILE = 'sha256'
BUCKET_NAME = os.environ['PROJECT_ID']
logger.log_text(f'Bucket name: {BUCKET_NAME}')

### create conversation thread
from conversation_thead import ConversationThread
convo_thread = ConversationThread()
logger.log_text(f'Created ConversationThread for PROJECT_ID: {PROJECT_ID}')

from data_loader import DataLoader
data_loader = DataLoader(BUCKET_NAME, HASH_FILE, INDEX_VECTOR_LOCAL_FILE, QUESTIONS_FILE)
logger.log_text(f'Created DataLoader for PROJECT_ID: {PROJECT_ID}')

convo_thread.index = data_loader.load_index()
logger.log_text(f'Loaded index for PROJECT_ID: {PROJECT_ID}')

convo_thread.suggested_questions = data_loader.load_questions()
logger.log_text(f'Loaded questions for PROJECT_ID: {PROJECT_ID}')

logger.log_text(f'Creating Flask app for PROJECT_ID: {PROJECT_ID}')
from flask import Flask
from flask_restful import Resource, Api, request, reqparse

app = Flask(__name__)
api = Api(app)
post_parser = reqparse.RequestParser()

class Responses(Resource):
	def get(self):
		args = request.args #retrieve args from query string
		user_id = args.get('user_id')
		query_str = args.get('query_str')
		convo_thread.answer_question(user_id, query_str)
		last_answer = convo_thread.get_last_answer(user_id)
		last_empty_response = convo_thread.get_last_empty_response(user_id)

		if last_empty_response:
			data_loader.append_blob(query_str)

		# check last_loaded_index_time
		# if last_loaded_index_time > 60 minutes
			# pull latest index from gcs and load

		"""
		t = time.time()
		diff = t - data_loader.last_loaded_index_time
		logger.log_text(f'secs since last index load: {diff}, query_str: {query_str}, last_answer: {last_answer}')

		if diff > MAX_SECS_TO_LOAD_INDEX:
			logger.log_text(f'{PROJECT_ID}: {diff} seconds since last index load; loading index')
			convo_thread.index = data_loader.load_index()
			convo_thread.suggested_questions = data_loader.load_questions()
		"""
		return {'response': last_answer}, 200  # return data and 200 OK code

api.add_resource(Responses, '/responses')

logger.log_text(f'Created Flask app for PROJECT_ID: {PROJECT_ID}')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
