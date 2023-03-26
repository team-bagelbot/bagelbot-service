from google.cloud import logging

class AppLogger():
	def __init__(self, name):
		self.name = name
		self.client = logging.Client().logger(name)

	def log_text(self, text):
		self.client.log_text(text)
		print(text)