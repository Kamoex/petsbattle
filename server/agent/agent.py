from . import llm
class agent:
    def __init__(self, system_prompt: str, stream: bool = False):
        self.system_prompt = system_prompt
        self.stream = stream
        self.messages = []

    def add_message(self, message: str):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    async def execute(self, content: str):
        if self.stream:
            return await llm.req_gpt_stream(self.system_prompt, content)
        else:
            result = await llm.req_gpt(self.system_prompt, content)
            self.add_message(content)
            self.add_message(result)
            return result