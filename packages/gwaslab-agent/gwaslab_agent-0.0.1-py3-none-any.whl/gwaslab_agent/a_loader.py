# ================================
# Standard Library
# ================================
import gzip
import os
import sys

# Add gwaslab source path
sys.path.insert(0, "/home/yunye/work/gwaslab/src")

# ================================
# Third-Party Libraries
# ================================
import numpy as np
import pandas as pd
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool

# ================================
# GWASLab
# ================================
import gwaslab as gl
from gwaslab.bd.bd_download import check_format, list_formats
from gwaslab.io.io_preformat_input import preformat

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.g_build_tools import _build_args_schema
from gwaslab_agent.g_console import console
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_sys_prompt import system_prompt_loader
from gwaslab_agent.g_wrap_tools import wrap_loader_method


def _is_figure(obj):
    """Detect Matplotlib figure or axes objects."""
    try:
        import matplotlib
        import matplotlib.figure
        import matplotlib.axes
    except ImportError:
        return False

    if isinstance(obj, matplotlib.figure.Figure):
        return True
    if isinstance(obj, matplotlib.axes.Axes):
        return True
    # sometimes Matplotlib returns a tuple like (fig, ax)
    if isinstance(obj, (list, tuple)) and any(
        isinstance(o, (matplotlib.figure.Figure, matplotlib.axes.Axes)) for o in obj
    ):
        return True
    return False

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )
    
def check_file_format_and_headers( file_path: str ):
    """Check file format based on extension and read first 5 lines.
    
    Args:
        file_path: Path to file to check
        
    Returns:
        Tuple of (format_extension, list_of_first_lines)
    """
    num_lines = 5

    _, ext = os.path.splitext(file_path)
        
    try:
        if ext == ".gz":
            with gzip.open(file_path, "rt") as f:
                lines = [next(f) for _ in range(num_lines)]
        else:
            with open(file_path, "r") as f:
                lines = [next(f) for _ in range(num_lines)]
                
        return ext, lines
    except Exception as e:
        raise IOError(f"Error reading file: {e}")

class SmartLoader():
    """
    LLM powered GWAS sumstats loader
    """
    def __init__(self,  llm=None, **kwargs):
        empty_data = pd.DataFrame()
        self.sumstats = gl.Sumstats(empty_data, verbose=False)
        self.archive = []
        self.history = [] 
        self.toolcalls = []
        self.log = self.sumstats.log
        self.full_schema = {}
        self.tool_docs = {}
        self.llm = llm
        
        self.log.write("Initiating GWASLab Agent Loader...")
        self.tools = self._build_tools_from_methods()
        self.agent = self._init_agent()

    def _build_tools_from_methods(self):
        tools = []
        ##############################################################################################
        name = "gl.Sumstats"
        method = gl.Sumstats
        detailed_docs, all_schema, schema  = _build_args_schema(preformat, if_sig=False)
        self.full_schema[name] = all_schema
        wrapped = self._wrap_method(name, method)

        tools.append(
            StructuredTool.from_function(
                func=wrapped,
                name=name,
                description=detailed_docs or "No description provided.",
                args_schema=schema,
            )
        )
        self.tool_docs[name] = detailed_docs
        ##############################################################################################
        ##############################################################################################



        name = "list_formats"
        method = list_formats
        detailed_docs, all_schema, schema  = _build_args_schema(list_formats, if_sig=False)
        self.full_schema[name] = all_schema
        wrapped = self._wrap_method(name, method)

        tools.append(
            StructuredTool.from_function(
                func=wrapped,
                name=name,
                description=detailed_docs or "No description provided.",
                args_schema=schema,
            )
        )
        self.tool_docs[name] = detailed_docs
        ##############################################################################################
        ##############################################################################################

        name = "check_format"
        method = check_format
        detailed_docs, all_schema, schema  = _build_args_schema(check_format, if_sig=False)
        self.full_schema[name] = all_schema
        wrapped = self._wrap_method(name, method)

        tools.append(
            StructuredTool.from_function(
                func=wrapped,
                name=name,
                description=detailed_docs or "No description provided.",
                args_schema=schema,
            )
        )
        self.tool_docs[name] = detailed_docs
        ##############################################################################################
        ##############################################################################################
        name = "check_file_format_and_read"
        method = check_file_format_and_headers
        detailed_docs, all_schema, schema  = _build_args_schema(method, if_sig=False)
        self.full_schema[name] = all_schema
        wrapped = self._wrap_method(name, method)

        tools.append(
            StructuredTool.from_function(
                func=wrapped,
                name=name,
                description=detailed_docs or "No description provided.",
                args_schema=schema,
            )
        )
        self.tool_docs[name] = detailed_docs


        ##############################################################################################
        ###############################################################################################
        #name = "infer_build"
        #method = self.sumstats.infer_build
        #detailed_docs, all_schema, schema  = _build_args_schema(method)
        #self.full_schema[name] = all_schema
        #wrapped = self._wrap_method(name, method)
#
        #tools.append(
        #    StructuredTool.from_function(
        #        func=wrapped,
        #        name=name,
        #        description=detailed_docs or "No description provided.",
        #        args_schema=schema,
        #    )
        #)
        #self.tool_docs[name] = detailed_docs
        ###############################################################################################
        #name = "infer_ancestry"
        #method = self.sumstats.infer_ancestry
        #detailed_docs, all_schema, schema  = _build_args_schema(method)
        #self.full_schema[name] = all_schema
        #wrapped = self._wrap_method(name, method)
#
        #tools.append(
        #    StructuredTool.from_function(
        #        func=wrapped,
        #        name=name,
        #        description=detailed_docs or "No description provided.",
        #        args_schema=schema,
        #    )
        #)
        #self.tool_docs[name] = detailed_docs
        ##############################################################################################
        self.log.write(f" -Registered {len(tools)} tools for SmartLoader.")
        return tools
    
    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_loader_method(self, name, method)
    
    def _init_toolcalls(self, message):
        self.toolcalls.append({"message":message,
                          "toolcalls":{}})
    def _add_toolcalls(self, toolcalls):
        self.toolcalls[-1]["toolcalls"] = toolcalls

    def _init_agent(self):
        
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    middleware=[handle_tool_errors],
                                    system_prompt=system_prompt_loader
                                )

    def run(self, message: str, verbose=True,verbose_return=False, return_message=False):

        self.history.append({"role": "user", "content": message})
        self._init_toolcalls(message)

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

                print_message(self, console, msg, step, return_message, verbose, verbose_return)
                if getattr(msg, "content", None):
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "content": msg.content})

    def new_run(self, message: str, verbose=True):
        self.history = []
        self.run(message)
