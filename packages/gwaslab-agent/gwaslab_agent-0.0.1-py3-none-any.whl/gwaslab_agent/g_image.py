# --- add at top of module ---
import json, re
from numbers import Number
import numpy as np
import pandas as pd

def _is_figure(obj):
    # Your existing check; add a few common libs if you like
    try:
        import matplotlib.figure as _mpl_fig
        if isinstance(obj, _mpl_fig.Figure):
            return True
    except Exception:
        pass
    try:
        import plotly.graph_objs as go
        if isinstance(obj, go.Figure):
            return True
    except Exception:
        pass
    try:
        from PIL import Image as _PILImage
        if isinstance(obj, _PILImage.Image):
            return True
    except Exception:
        pass
    # ndarray that "looks like" an image
    if isinstance(obj, np.ndarray) and obj.ndim in (2, 3) and obj.size > 0:
        if obj.ndim == 2 or (obj.ndim == 3 and obj.shape[2] in (1, 3, 4)):
            return True
    return False

def _show_locally(obj):
    """Render fig/image in a Jupyter/IPython notebook (no return)."""
    try:
        from IPython.display import display
        # Matplotlib
        try:
            import matplotlib.figure as _mpl_fig
            import matplotlib.pyplot as plt
            if isinstance(obj, _mpl_fig.Figure):
                display(obj)
                plt.close(obj)  # free memory; keeps the displayed output
                return
        except Exception:
            pass
        # Plotly
        try:
            import plotly.graph_objs as go
            if isinstance(obj, go.Figure):
                # display() avoids sending a giant dict to the LLM channel
                display(obj)
                return
        except Exception:
            pass
        # PIL
        try:
            from PIL import Image as _PILImage
            if isinstance(obj, _PILImage.Image):
                display(obj)
                return
        except Exception:
            pass
        # NumPy image-like
        if isinstance(obj, np.ndarray):
            try:
                from PIL import Image as _PILImage
                if obj.ndim == 2:
                    display(_PILImage.fromarray(obj))
                    return
                if obj.ndim == 3 and obj.shape[2] in (1, 3, 4):
                    # Convert single-channel to 2D, others directly
                    if obj.shape[2] == 1:
                        display(_PILImage.fromarray(obj[:, :, 0]))
                    else:
                        display(_PILImage.fromarray(obj))
                    return
            except Exception:
                pass
        # As a last resort, try generic display
        display(obj)
    except Exception:
        # If not in IPython / cannot display, just swallow
        pass

def _scrub_log(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "[image:data-url-redacted]", text)
    text = re.sub(r"[A-Za-z0-9+/]{200,}={0,2}", "[possible-binary-redacted]", text)
    text = re.sub(r"<Figure[^>]*>", "[matplotlib-figure-redacted]", text)
    return text.strip()