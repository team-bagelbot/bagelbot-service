import os
import sys

# Add the top-level project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from conversation_thead import ConversationThread
convo_thread = ConversationThread()

class TestConversationThread(unittest.TestCase):

    def setUp(self):
        convo_thread.store = {
            'user1': [
                {'answer': 'answer1', 'question': 'question1', 'is_empty_response': False},
                {'answer': 'answer2', 'question': 'question2', 'is_empty_response': False}
            ],
            'user2': []
        }
        
    def test_existing_user_with_answers(self):
        user_id = 'user1'
        expected_answer = 'answer2'
        actual_answer = convo_thread.get_last_answer(user_id)
        self.assertEqual(expected_answer, actual_answer)
        
    def test_existing_user_without_answers(self):
        user_id = 'user2'
        expected_answer = ''
        actual_answer = convo_thread.get_last_answer(user_id)
        self.assertEqual(expected_answer, actual_answer)
        
    def test_nonexistent_user(self):
        user_id = 'user3'
        expected_answer = ''
        actual_answer = convo_thread.get_last_answer(user_id)
        self.assertEqual(expected_answer, actual_answer)
        
if __name__ == '__main__':
    unittest.main()
