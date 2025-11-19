from gwaslab.g_Log import Log
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from gwaslab_agent.g_sys_prompt import system_prompt_summarizer
from gwaslab_agent.g_build_tools import _build_tools_from_methods, handle_tool_errors
from gwaslab_agent.g_print import print_message

class Summarizer():
    def __init__(self, log_object, toolcalls=None, llm=None):
        self.log = log_object
        self.log.write("Initiating GWASLab Agent Summarizer...")
        self.archive = []
        
        self.toolcalls = toolcalls
        self.llm = llm
        
        self.agent = self._init_agent()

    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    system_prompt=system_prompt_summarizer
                                )
        
    def _compose_log_message(self, message):
        return """Toocalls:{}\n\nSumstats log:\n{}\n\nGWASLab worker message:{}""".format(self.toolcalls, 
                                                                                          self.log.log_text, 
                                                                                          message)

    def run(self, message: str, history=None, verbose=True, return_message=False, verbose_return=False, message_to_return=None):
        
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
        
        if history is None:
            self.history = [] 
        else:
            self.history = history

        self.history.append({"role": "user", 
                             "content": self._compose_log_message(message)})

        for chunk in self.agent.stream(
            {"messages": self.history},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                #print(step, data)
                msg = messages[-1]

                message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return, title="SUMMARIZER")
                if getattr(msg, "content", None):
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "content": msg.content})
        
        if return_message == True:
            return message_to_return

    def new_run(self, message: str):
        self.history = []
        self.run(message)
