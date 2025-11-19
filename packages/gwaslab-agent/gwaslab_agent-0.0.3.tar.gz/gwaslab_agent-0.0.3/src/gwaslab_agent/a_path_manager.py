import numpy as np
import pandas as pd
import gwaslab as gl
import inspect
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from gwaslab_agent.g_sys_prompt import system_prompt_path
from gwaslab_agent.g_build_tools import _build_args_schema, handle_tool_errors
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_wrap_tools import wrap_main_agent_method

class PathManager():
    def __init__(self, log_object, llm=None):
        self.log = log_object
        self.log.write("Initiating GWASLab Agent Path Manager...")
        self.archive = []
        self.history = [] 
        self.toolcalls = []
        self.tool_docs={}
        self.tools = self._build_tools_from_methods()
        self.llm = llm
        
        self.agent = self._init_agent()

    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    system_prompt=system_prompt_path,
                                    middleware=[handle_tool_errors]
                                )
        
    def _compose_log_message(self, message):
        return """Sumstats log:\n{}\n\nUser message:{}""".format(self.log.log_text, message)
    
    def _build_tools_from_methods(self):
        tools = []
        ##############################################################################################
        included_tools=["scan_downloaded_files", 
                        "check_available_ref",
                        "remove_local_record",
                        "add_local_data",
                        "check_downloaded_ref", 
                        "download_ref"]
        ## scan_downloaded_files download_ref
        for name, method in inspect.getmembers(gl, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            if name not in included_tools:
                continue
            detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
            wrapped = self._wrap_method(name, method)

            tools.append(
                StructuredTool.from_function(
                    func=wrapped,
                    name=name,
                    description=inspect.getdoc(method) or "No description provided.",
                    args_schema=schema,
                )
            )
            self.tool_docs[name] = detailed_docs
        self.log.write(f" -Registered {len(tools)} tools for PathManager.")
        return tools


    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_main_agent_method(self, name, method)
    
    def _init_toolcalls(self, message):
        self.toolcalls.append({"message":message,
                          "toolcalls":{}})
    def _add_toolcalls(self, toolcalls):
        self.toolcalls[-1]["toolcalls"] = toolcalls

    def run(self, message: str, verbose=True, verbose_return=False, return_message=True, if_print=True, message_to_return=None):
        self._init_toolcalls(message)
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
        
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

                message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return, if_print=if_print, title="SUMMARIZER")
                if getattr(msg, "content", None):
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "content": msg.content})
        if return_message == True:
            return message_to_return
        
    def new_run(self, message: str):
        self.history = []
        self.run(message)
