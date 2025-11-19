import pandas as pd
import json
import json
import numpy as np
from numbers import Number
import json, re
import gwaslab as gl

def wrap_loader_method(self, name, method):
    """Wrap a method for LLM-safe, structured output serialization."""
    def wrapped(**kwargs):
        try:
            previous_log_end = len(self.log.log_text)
            result = method(**kwargs)
            self.archive.append(result)
            new_log = self.log.log_text[previous_log_end + 1:]
            
            # --- DataFrame or Series ---
            if isinstance(result, gl.Sumstats):
                out_type = "gl.Sumstats"
                data_string = "Sumstats has been successfully loaded."
                self.sumstats_new = result
                self.sumstats.data = self.sumstats_new.data
                self.log = self.sumstats.log = self.sumstats_new.log
                self.sumstats.meta = self.sumstats_new.meta
                self.sumstats.build = self.sumstats_new.build
                return json.dumps({
                "status": "success",
                "method": name,
                "type": out_type,
                "data": data_string,
                "log": new_log.strip() if new_log else ""
                                }, ensure_ascii=False)

            elif isinstance(result, pd.Series):
                data = result.to_dict()
                out_type = "Series"

            # --- NumPy array ---
            elif isinstance(result, np.ndarray):
                data = result.tolist()
                out_type = "ndarray"

            # --- Tuple or list ---
            elif isinstance(result, (list, tuple)):
                data = result
                out_type = type(result).__name__

            # --- Dict ---
            elif isinstance(result, dict):
                data = result
                out_type = "dict"

            # --- Single number ---
            elif isinstance(result, Number):
                data = result
                out_type = "number"

            # --- String-like ---
            elif isinstance(result, str):
                data = result
                out_type = "string"

            # --- None or void return ---
            elif result is None:
                data = "✅ Executed successfully (no return value)."
                out_type = "none"

            # --- Fallback: attempt JSON serialization ---
            else:
                try:
                    data = json.loads(json.dumps(result, default=str))
                    out_type = "unknown_jsonable"
                except Exception:
                    data = str(result)
                    out_type = "string_fallback"

            # --- Return consistent JSON ---
            return json.dumps({
                "status": "success",
                "method": name,
                "type": out_type,
                "data": data,
                "log": new_log.strip() if new_log else ""
            }, ensure_ascii=False)

        except Exception as e:
            # In case the method itself fails
            err_log = ""
            if hasattr(self.log, "getvalue"):
                err_log = self.log.getvalue()
            return json.dumps({
                "status": "error",
                "method": name,
                "error": str(e),
                "log": err_log.strip()
            }, ensure_ascii=False)
    return wrapped




from gwaslab_agent.g_image import _scrub_log
from gwaslab_agent.g_image import _show_locally
from gwaslab_agent.g_image import _is_figure
def wrap_main_agent_method(self, name, method):
    """Wrap a method for LLM-safe, structured output serialization."""
    def wrapped(**kwargs):
        try:
            previous_log_end = len(self.log.log_text)
            result = method(**kwargs)

            self.archive.append(result)
            new_log = self.log.log_text[previous_log_end + 1:]
            new_log = _scrub_log(new_log)

            # Resolve your handle → real object (unchanged)
            if isinstance(result, dict) and "subset_id" in result:
                obj_id = result["subset_id"]
                obj = self.FILTERED_SUMSTATS.get(obj_id)
                result = obj

            # --- If it's a figure/image: SHOW LOCALLY but NEVER return the image ---
            if _is_figure(result):
                _show_locally(result)  # renders in Jupyter
                return json.dumps({
                    "status": "success",
                    "method": name,
                    "type": "image_redacted",
                    "data": "Image/figure shown in notebook; content withheld from LLM.",
                    "log": new_log
                }, ensure_ascii=False)

            # --- Your existing branches (unchanged except for log scrubbing) ---
            if isinstance(result, gl.Sumstats):
                obj_id = self.FILTERED_SUMSTATS.put(result)
                new_log = self.FILTERED_SUMSTATS.get(obj_id).log.log_text[previous_log_end + 1:]
                return {
                    "status": "success",
                    "type": "filtered Sumstats object",
                    "instructions": (
                        "Access using "
                        "`run_filtered` for visualization and processing."
                    ),
                    "subset_id": obj_id,
                    "log": _scrub_log(new_log),
                }

            if isinstance(result, pd.DataFrame):
                if isinstance(result.index, pd.MultiIndex):
                    result = result.reset_index()
                data = result.to_dict(orient="index")
                out_type = "DataFrame"

            elif isinstance(result, pd.Series):
                data = result.to_dict()
                out_type = "Series"

            elif isinstance(result, np.ndarray):
                # If ndarray looks like an image, still render locally and redact
                if _is_figure(result):
                    _show_locally(result)
                    return json.dumps({
                        "status": "success",
                        "method": name,
                        "type": "image_redacted",
                        "data": "Image/figure shown in notebook; content withheld from LLM.",
                        "log": new_log
                    }, ensure_ascii=False)
                data = result.tolist()
                out_type = "ndarray"

            elif isinstance(result, (list, tuple)):
                data = result
                out_type = type(result).__name__

            elif isinstance(result, dict):
                data = result
                out_type = "dict"

            elif isinstance(result, Number):
                data = result
                out_type = "number"

            elif isinstance(result, str):
                data = result
                out_type = "string"

            elif result is None:
                data = "Executed successfully (no return value)."
                out_type = "none"

            else:
                try:
                    data = json.loads(json.dumps(result, default=str))
                    out_type = "unknown_jsonable"
                except Exception:
                    data = str(result)
                    out_type = "string_fallback"

            return json.dumps({
                "status": "success",
                "method": name,
                "type": out_type,
                "data": data,
                "log": new_log
            }, ensure_ascii=False)

        except Exception as e:
            err_log = ""
            if hasattr(self.log, "getvalue"):
                err_log = self.log.getvalue()
            return json.dumps({
                "status": "error",
                "method": name,
                "error": str(e),
                "log": _scrub_log(err_log)
            }, ensure_ascii=False)
    return wrapped