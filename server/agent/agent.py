
class agent:
    def __init__(self, system_prompt: str, stream: bool = False):
        self.system_prompt = system_prompt
        self.stream = stream
        self.messages = []

    def add_message(self, message: str):
        self.messages.append(message)

    def get_messages(self):
        return self.messages
        pass

    def execute(self, content: str):
        pass