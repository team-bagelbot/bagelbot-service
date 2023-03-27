from llama_index import QuestionAnswerPrompt

EMPTY_RESPONSE = 'Empty Response'
MAIN_SUBJECT = 'bagels'
MAX_STORE_LENGTH = 3

class ConversationThread():
    def __init__(self) -> None:
        self.index = None
        self.suggested_questions = None
        self.store = {}
        self.max_store_length = MAX_STORE_LENGTH

    def answer_question(self, user_id: str, query_str: str) -> None:
        """
        Takes a user ID and a query string as input, processes the user's question, generates a response,
        confirms that the response is not empty, and saves the question-answer pair to the conversation thread.

        Args:
        -----
        user_id: (str)
            A string representing the ID of the user asking the question.
        query_str: (str)
            A string representing the question that the user is asking.

        Returns:
        --------
        None
        """
        last_thread = self._build_last_thread(user_id)
        text_qa_prompt = self._build_qa_template(last_thread)

        response = self.index.query(query_str,
            text_qa_template=text_qa_prompt,
			mode='default',
			similarity_top_k=1)
        confirmed_response = self._check_empty_response(response)

        data = {
            "question": query_str,
            "answer": str(confirmed_response).strip(),
            "is_empty_response": confirmed_response != response
        }
        self._add_to_thread(user_id, data)

    def get_last_answer(self, user_id: str) -> str:
        '''
        Retrieves the last answer stored for a given user.

        Args:
        -----
        user_id (str):
            The unique identifier for the user whose last answer is to be retrieved.

        Returns:
        --------
        str:
            The last answer stored for the given user, or an empty string if no answer has been stored for the user or the user does not exist in the store.
        '''
        if not user_id in self.store:
            return ""
        if len(self.store[user_id]) == 0:
            return ""
        return self.store[user_id][-1]['answer']
    
    def get_last_empty_response(self, user_id: str) -> str:
        if not user_id in self.store:
            return ""
        if len(self.store[user_id]) == 0:
            return ""
        return self.store[user_id][-1]['is_empty_response']

    def _add_to_thread(self, user_id: str, item: dict) -> None:
        '''
        Adds an item to the conversation thread for a specific user and removes 
        the oldest item if the maximum store length has been reached.

        Args:
        -----
        user_id (str):
            The ID of the user to add the item to their conversation thread.
        item (dict):
            The item to add to the conversation thread.

        Returns:
        --------
        None. The function only modifies the store dictionary of the ConversationThread instance.
        '''
        self.store[user_id].append(item)
        self._remove_oldest_store_item(self.store[user_id])

    def _remove_oldest_store_item(self, arr: list) -> None:
        if len(arr) > self.max_store_length:
            arr.pop(0)

    def _get_answer_store_length(self, user_id: str) -> int:
        if not user_id in self.store:
            return 0
        return len(self.store[user_id]['answers'])
    
    def _build_last_thread(self, user_id: str) -> str:
        ### TODO: check if this conversation has timed out
        if not user_id in self.store:
            self.store[user_id] = []
        thread = ""
        for i in range(len(self.store[user_id])):
            thread += f"Q: {self.store[user_id][i]['question']}\n"
            thread += f"A: {self.store[user_id][i]['answer']}\n\n"
        return thread

    def _build_qa_template(self, last_thread: str) -> QuestionAnswerPrompt:
        text_qa_template = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            "If you cannot answer the last question using only the context information, "
            f"respond with '{EMPTY_RESPONSE}'\n"
            f"{last_thread}\n"
            "Q: {query_str}\n"
            "A:\n"
        )
        return QuestionAnswerPrompt(text_qa_template)

    def _check_empty_response(self, response: str) -> str:
        if str(response).lower().find(EMPTY_RESPONSE.lower()) != -1:
            response = (
                f"I'm trained only on specific information about {MAIN_SUBJECT} and "
                "do not have enough information to answer your question. Try some "
                f"of these questions: \n{self.suggested_questions}"
            )
        return response
