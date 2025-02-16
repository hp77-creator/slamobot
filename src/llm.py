import google.generativeai as genai



class LLM:
    def __init__(self, API_KEY, model_name):
        self.api_key = API_KEY  #change for other models
        self.model_name = model_name
    
    def change_model(self, new_model):
        if new_model not in genai.list_models:
            raise Exception("This model is currently not supported")
        self.model = new_model
    
    def get_base_model(self):
        genai.configure(self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        return self.model 
    
    def chat_with_history(self, history=[]):
        self.chat = self.get_base_model().start_chat(history=history)
    
    def get_chat_response(self, prompt):
        self.chat_with_history()
        return self.chat.send_message(prompt)