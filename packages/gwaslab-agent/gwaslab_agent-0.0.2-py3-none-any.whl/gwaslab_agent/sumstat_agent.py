# ================================
# Standard Library
# ================================
import os
import sys
from numbers import Number
from typing import get_type_hints

# ================================
# GWASLab
# ================================
import gwaslab as gl
from gwaslab.g_Log import Log
# ================================
# Third-Party Libraries
# ================================
import numpy as np
import pandas as pd
from langchain.agents import create_agent

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.a_loader import SmartLoader
from gwaslab_agent.a_path_manager import PathManager
from gwaslab_agent.a_planner import Planner
from gwaslab_agent.a_summarizer import Summarizer
from gwaslab_agent.g_build_tools import (
    _build_tools_from_methods,
    handle_tool_errors,
    retry_tool_wrapper,
    FILTERED_SUMSTATS,
)
from gwaslab_agent.g_console import console
from gwaslab_agent.g_llm import get_llm
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_sys_prompt import system_prompt
from gwaslab_agent.g_wrap_tools import wrap_main_agent_method
from gwaslab_agent.g_version import _show_version

class SmartSumstats():
    """
    Extended version of gwaslab.Sumstats that:
      - Behaves exactly like the original Sumstats
      - Can build JSON Schemas for its methods using a parameter table
      - Embeds an internal LLM agent that can call its own methods via chat
    """
    def __init__(self, path: str, llm_configuration=None, **kwargs):
        
        self.log = Log()
        self.log.write("Initiating GWASLab Agent...")
        _show_version(self.log)
        self.llm = get_llm(self.log)
        self.toolcalls = []

        if not os.path.exists(path):
            self.sl = SmartLoader(llm=self.llm)
            self.sl.run(path)
            self.sumstats = self.sl.sumstats
            self.toolcalls.extend(self.sl.toolcalls)
        else:
            self.sumstats = gl.Sumstats(path, **kwargs)

        self.config = gl.options
        self.sumstats.log.combine(self.log)
        self.log = self.sumstats.log
        self.archive = []
        self.history = [] 
        
        self.FILTERED_SUMSTATS = FILTERED_SUMSTATS

        # full args schema for tools
        self.full_schema = {}
        self.tool_docs = {}

        self.log.write("Initiating GWASLab Agent Worker...")
        # only main args were loaded for tools; full args are stored in self.full_schema; descriptions are stored in self.tool_docs.
        self.tools = _build_tools_from_methods(self)
        self.agent = self._init_agent()
        self.planner = Planner(self.log, self.tools, llm = self.llm)
        self.pathmanager = PathManager(self.log, llm = self.llm)
        self.summarizer = Summarizer(self.log, llm = self.llm, toolcalls = self.toolcalls)
        self.log.write("Finished loading...")

    def get_reference_file_path(self, description):
        """
        Search reference file path for downstream processes and visualization. Search is conducted by GWASLab PathManager agent.

        Parameters
        --------------------------
        description: str
            A short description of the file.
        """
        return self.pathmanager.run("Find file path based the description:\n{}".format(description))
        
    def run_filtered(self, object_id: str, tool_name: str, *args, **kwargs):
        """
        Call a tool on a filtered Sumstats object stored in FILTERED_SUMSTATS. Usually used for visualization after filtering using `filter_xxx` tools.

        Examples
        --------
        # Call a method without arguments:
        run_filtered("subset_0", "plot_density")

        # Call a method with arguments:
        run_filtered("subset_1", "plot_mqq", sig=5e-8)

        Parameters
        ----------
        object_id : str
            The ID of the filtered Sumstats object inside FILTERED_SUMSTATS.
        tool_name : str
            The name of the Sumstats method to call.
        *args :
            Positional arguments to pass to the method.
        **kwargs :
            Keyword arguments to pass to the method.

        Returns
        -------
        dict or object
            - If the tool returns a new Sumstats object, a new subset ID is returned.
            - Otherwise, the actual result of the tool call is returned.
            - Errors are caught and returned as {"error": "..."}.
        """

        try:
            # Retrieve object
            obj = self.FILTERED_SUMSTATS.get(object_id)
            if obj is None:
                return {"error": f"Object ID '{object_id}' not found in FILTERED_SUMSTATS."}

            # Ensure the tool exists
            if not hasattr(obj, tool_name):
                return {"error": f"Method '{tool_name}' does not exist on this Sumstats object."}

            method = getattr(obj, tool_name)

            # Execute the method
            result = method(*args, **kwargs)

            return result

        except Exception as e:
            return {"error": str(e)}
    
    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_main_agent_method(self, name, method)
    
    def __getattr__(self, name):
        """
        Forward unknown attributes or methods to the wrapped Sumstats object.
        This makes SmartSumstats act like a normal Sumstats.
        """
        return getattr(self.sumstats, name)
    # =========================================================
    # 2️⃣ Dynamically expose methods as tools
    # =========================================================
    
    def search_full_docs(self, tool_name: str) -> str:
        """
        When needed, call search_full_docs(tool_name= tool_name) to get detailed descriptions and arguments!
#
        Parameters: 
            tool_name: tool_name
        """
        return {"description":self.tool_docs[tool_name], "args":self.full_schema[tool_name]}
    def get_template_script_for_tools(self, tool_name: str) -> str:
        """
        Search script_library for a Python file containing the specified tool name in its first line.
        Returns the file content if found, or an error message if not found.
        """
        script_dir = "src/gwaslab_agent/script_library"
        try:
            for filename in os.listdir(script_dir):
                if filename.endswith(".py"):
                    file_path = os.path.join(script_dir, filename)
                    with open(file_path, 'r') as file:
                        first_line = file.readline().strip()
                        if first_line.startswith('#methods:'):
                            methods = first_line.split(':', 1)[1].strip().split(',')
                            methods = [m.strip() for m in methods]
                            if tool_name in methods:
                                return file.read()
            return f"No script found for tool '{tool_name}'"
        except Exception as e:
            return f"Error searching scripts: {str(e)}"
    #LLMToolSelectorMiddleware(model= self.llm,   max_tools= 15)
    # =========================================================
    # 3️⃣ Build the internal agent
    # =========================================================
    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    middleware=[handle_tool_errors, 
                                                retry_tool_wrapper(max_retries = 3)
                                                ],
                                    system_prompt=system_prompt
                                )
    
    

    def _init_toolcalls(self, message):
        self.toolcalls.append()
    def _add_toolcalls(self, toolcalls):
        self.toolcalls[-1]["toolcalls"] = toolcalls
        
    def run(self, message: str, 
            verbose=True, 
            verbose_return=False, 
            return_message=False):
        
        message_to_return =""

        self.history.append({"role": "user", "content": message})

        for chunk in self.agent.stream(
            {"messages": self.history},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                msg = messages[-1]

                message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return)

                if getattr(msg, "content", None):
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "content": msg.content})

        if return_message == True:
            return message_to_return
    
    def new_run(self, message: str):
        self.history = []
        self.run(message)

    def plan_run(self, message: str):
        self.history = []
        self.planner.history = []
        message = self.planner.run(message)
        message = self.run(message)
    
    def new_plan_run(self, message: str):
        self.history = []
        self.planner.history = []
        message = self.planner.run(message)
        self.run(message)

    def new_plan(self, message: str):
        self.planner.history = []
        message = self.planner.run(message)

    def plan_run_sum(self, message: str):
        message = self.planner.run(message)
        message = self.run(message, 
                           return_message=True)
        self.summarizer.run(message)

    def new_plan_run_sum(self, message: str):
        self.history = []
        self.planner.history = []
        self.summarizer.history = []
        message = self.planner.run(message)
        message = self.run(message, 
                           return_message=True)
        self.summarizer.run(message)

    def sum(self, message):
        self.summarizer.run(message)

    def clear(self, pl=False, 
                            w=True, 
                            pm=False, 
                            s=False):
        if pl == True:
            self.planner.history = []
        if w == True:
            self.history = []
        if pm == True:
            self.pathmanager.history = []
        if s == True:
            self.summarizer.history = []