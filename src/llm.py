import google.generativeai as genai



class LLM:
    def __init__(self, API_KEY, model_name):
        self.api_key = API_KEY  #change for other models
        self.model_name = model_name
        self.chat = None

        if 'gemini' in model_name.lower():
            genai.configure(self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            raise NotImplementedError(f"Model {model_name} is not supported yet")
    

    def change_model(self, new_model):
        if 'gemini' in new_model.lower():
            available_models = [model.name for model in genai.list_models()]
            if new_model not in available_models:
                raise ValueError(f"Model {new_model} is not available. Available Models: {available_models}")
            self.model_name = new_model
            self.model = genai.GenerativeModle(new_model)
            self.chat = None
        else:
            raise NotImplementedError(f"Model {new_model} not added yet.")
    
    def chat_with_history(self, history=[]):
        if history is None:
            history = []
        if 'gemini' in self.model_name.lower():
            self.chat = self.model.start_chat(history=history)
        else:
            raise NotImplementedError("Chat with history not implemented yet.")
    
    def get_chat_response(self, prompt):
        try:
            if self.chat is None:
                self.chat_with_history()
            
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error getting chat response: {str(e)}")