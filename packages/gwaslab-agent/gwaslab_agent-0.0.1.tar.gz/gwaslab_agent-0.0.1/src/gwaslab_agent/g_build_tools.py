# ===== Standard Library =====
import inspect
import json
import os
import sys
from numbers import Number
from typing import get_type_hints

# ===== Third-Party Libraries =====
import numpy as np
import pandas as pd
from langchain.agents.middleware import after_model, wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool

# ===== Project: GWASLab =====
import gwaslab as gl

# ===== Project: GWASLab Agent =====
from gwaslab_agent.g_docstring_parser import parse_numpy_style_params
from gwaslab_agent.g_object_store import ObjectStore

FILTERED_SUMSTATS = ObjectStore()

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

from langchain_core.messages import AIMessage
import json5
import json

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
    
def retry_tool_wrapper(max_retries=3):
    """Return a wrap_tool_call function that retries failed tool calls."""
    @wrap_tool_call
    def wrapper(request, handler):
        tool_name = request.tool_call["name"]   # FIXED
        retries = 0

        while True:
            try:
                return handler(request)

            except Exception as e:
                retries += 1

                if retries >= max_retries:
                    return ToolMessage(
                        content=(
                            f"Tool error: `{tool_name}` failed after "
                            f"{max_retries} retries. Last error: {e}"
                        ),
                        tool_call_id=request.tool_call["id"]
                    )

                print(f"[Tool Retry] {tool_name}: attempt {retries}/{max_retries}")

    return wrapper

def _build_tools_from_methods(self):
    tools = []
    ########################################################################################################
    # gl.Sumstats
    excluded_tools = ["run_scdrs",
                      "run_prscs",
                      "run_magma",
                      "abf_finemapping",
                      "anno_gene",
                      "align_with_template",
                      "calculate_ld_matrix",
                      "check_ref",
                      "extract_ld_matrix",
                      "plot_pipcs",
                      "reload",
                      "get_beta",
                      "read_pipcs",
                      "calculate_prs",
                      "check_cs_overlap",
                      "get_cs_lead",
                      "offload",
                      "run_susie_rss",
                      "estimate_rg_by_ldsc",
                      "check_novel_set",
                      "check_cis",
                      "plot_gwheatmap",
                      "rsid_to_chrpos",
                      "rsid_to_chrpos2"
                        ]
    for name, method in inspect.getmembers(self.sumstats, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        if name in excluded_tools:
            continue
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
    ########################################################################################################
    # global
    #excluded_tools = ["get_path","check_available_ref","scatter","run_susie_rss","update_available_ref","update_formatbook","update_record","remove_file"
    #                    "read_popcorn","read_ldsc","rank_based_int","process_vcf_to_hfd5","plot_stacked_mqq","plot_miami2","plot_miami",
    #                    "plot_forest","meta_analyze","load_pickle","h2_se_to_p","h2_obs_to_liab","get_power","download_ref","reset_option","scan_downloaded_files",
    #                    "remove_file","read_tabular"  ,"read_popcorn","dump_pickle","gwascatalog_trait","compare_effect","plot_rg","plot_power_x"
    #                ]
    #for name, method in inspect.getmembers(gl, predicate=inspect.isfunction):
    #    if name.startswith("_"):
    #        continue
    #    if name in excluded_tools:
    #        continue
    #    detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
    #    self.full_schema[name] = all_schema
    #    wrapped = self._wrap_method(name, method)
#
    #    tools.append(
    #        StructuredTool.from_function(
    #            func=wrapped,
    #            name=name,
    #            description=inspect.getdoc(method) or "No description provided.",
    #            args_schema=schema,
    #        )
    #    )
    #    self.tool_docs[name] = detailed_docs
    ########################################################################################################
    # gl.config
    #excluded_tools=["set_option"]
    #for name, method in inspect.getmembers(self.config, predicate=inspect.ismethod):
    #    if name.startswith("_"):
    #        continue
    #    if name in excluded_tools:
    #        continue
    #    detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
    #    self.full_schema[name] = all_schema
    #    wrapped = self._wrap_method(name, method)
    #    tools.append(
    #        StructuredTool.from_function(
    #            func=wrapped,
    #            name=name,
    #            description=inspect.getdoc(method) or "No description provided.",
    #            args_schema=schema,
    #        )
    #    )
    #    self.tool_docs[name] = detailed_docs

    ########################################################################################################
    detailed_docs, all_schema, schema  = _build_args_schema(self.run_filtered, if_sig=False)
    wrapped = self._wrap_method("run_filtered", self.run_filtered)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="run_filtered",
            description=detailed_docs,
            args_schema=schema
        )
    )
    ########################################################################################################
    #wrapped = self._wrap_method("search_full_docs", self.search_full_docs)
    #tools.append(
    #    StructuredTool.from_function(
    #        func=wrapped,
    #        name="search_full_docs",
    #        description='Search full documentations including descriptions and arguments for a tool',
    #        args_schema={"tool_name": {"type": "string","description": "tool_name", "eum":list(self.tool_docs.keys())}}
    #    )
    #)
    #########################################################################################################
    #wrapped = self._wrap_method("get_template_script_for_tools", self.get_template_script_for_tools)
    #tools.append(
    #    StructuredTool.from_function(
    #        func=wrapped,
    #        name="get_template_script_for_tools",
    #        description='get examples on how to use a tool',
    #        args_schema={"tool_name": {"type": "string","description": "tool_name", "eum":list(self.tool_docs.keys())}}
    #    )
    #)
    ########################################################################################################
    wrapped = self._wrap_method("get_reference_file_path", self.get_reference_file_path)
    detailed_docs, all_schema, schema = _build_args_schema(self.get_reference_file_path, if_sig=False)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="get_reference_file_path",
            description=detailed_docs,
            args_schema=schema
        )
    )

    ########################################################################################################
    ########################################################################################################
    self.log.write(f" -Registered {len(tools)} tools for Worker and Planner...")
    return tools

def _build_args_schema(func, if_sig=True):
    import inspect
    from typing import get_type_hints

    sig = inspect.signature(func)
    hints = get_type_hints(func)
    
    # Parse NumPy-style docstring parameters
    parsed_dict = parse_numpy_style_params(func)
    doc_description  = parsed_dict["description"]
    doc_params_main =  parsed_dict["main_parameters"]
    doc_params_all =  parsed_dict["parameters"]
    
    props, required = {}, []

    # ------------------------------------------------------------
    # 1) Start from DOC PARAMS (these define the primary argument set)
    # ------------------------------------------------------------
    for name, info in doc_params_main.items():
        arg_schema = {}

        # Always preserve full info dictionary
        arg_schema = dict(info)

        # --------------------------------------------------
        # FIX: invalid defaults for array type
        # --------------------------------------------------
        if arg_schema.get("type") == "array":
            # Azure does NOT allow boolean defaults on array fields
            if isinstance(arg_schema.get("default"), bool):
                arg_schema["default"] = []

            # Null defaults also not ideal for array (Azure sometimes rejects)
            if arg_schema.get("default") is None:
                arg_schema["default"] = []

        # --------------------------------------------------
        # FIX: object defaults must be null or {}
        # --------------------------------------------------
        if arg_schema.get("type") == "object":
            if arg_schema.get("default") in (True, False):
                arg_schema["default"] = None
        #arg_schema = {}

        # directly from docstring
        #if info["description"]:
        #    arg_schema["description"] = info["description"]
        #if info["type"]:
        #    arg_schema["type"] = info["type"]
        #if info["default"] is not None:
        #    arg_schema["default"] = info["default"]
        # Fix invalid defaults for object-type fields

        # supplement type from type hints
        if "type" not in arg_schema and name in hints:
            arg_schema["type"] = hints[name].__name__
        
        if arg_schema.get("type") == "object" and isinstance(arg_schema.get("default"), bool):
            arg_schema["default"] = None

        # supplement default from function signature
        if name in sig.parameters:
            param = sig.parameters[name]
            if "default" not in arg_schema and param.default is not inspect.Parameter.empty:
                arg_schema["default"] = param.default
    
        
        # determine required
        if "default" not in arg_schema:
            required.append(name)

        props[name] = arg_schema

        if "required" in arg_schema:
            del arg_schema["required"]
    # ------------------------------------------------------------
    # 2) Handle parameters *present in signature but absent in docstring*
    # ------------------------------------------------------------
    if if_sig:
        for name, param in sig.parameters.items():
            if name in ("self", "kwargs", "insumstats", "kwreadargs", *doc_params_main.keys()):
                continue

            arg_schema = {}

            # type from type hint
            if name in hints:
                arg_schema["type"] = hints[name].__name__
            else:
                arg_schema["type"] = "string"

            # default from signature
            if param.default is not inspect.Parameter.empty:
                arg_schema["default"] = param.default
            else:
                required.append(name)

            props[name] = arg_schema

    return doc_description, doc_params_all, {"type": "object", "properties": props, "required": required}

def _build_args_schema_gwaslab(func):
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    props, required = {}, []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        hint = hints.get(name, str)
        props[name] = {"type": "string"}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}

