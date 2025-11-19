import inspect
import json, re

def parse_docstring_params(func):
    """
    Return {arg_name: description} extracted from docstring.
    Supports NumPy/SciPy style docstrings.
    """
    doc = inspect.getdoc(func) or ""
    if "Parameters" not in doc:
        return {}

    # Take only the block under "Parameters"
    try:
        params_block = doc.split("Parameters", 1)[1]
    except:
        return {}

    # Split into lines and clean
    lines = [l.rstrip() for l in params_block.splitlines()]

    params = {}
    current_arg = None
    buf = []

    for line in lines:
        # Pattern for arg definition line, e.g. "s : float"
        m = re.match(r"^\s*([A-Za-z0-9_]+)\s*:", line)
        if m:
            # flush previous
            if current_arg and buf:
                params[current_arg] = " ".join(buf).strip()
            current_arg = m.group(1)
            buf = []
        else:
            # description line
            if current_arg and line.strip():
                buf.append(line.strip())

    # flush last one
    if current_arg and buf:
        params[current_arg] = " ".join(buf).strip()

    return params
def split_docstring(doc):
    if doc is None:
        return "", ""
    
    lines = doc.strip().splitlines()
    
    if not lines:
        return "", ""

    one_liner = lines[0].strip()

    # Find the first blank (whitespace-only) line as separator
    blank_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if not line.strip():   # empty or whitespace-only
            blank_idx = i
            break

    if blank_idx is None:
        detailed = ""
    else:
        detailed = "\n".join(lines[blank_idx+1:]).strip()
    print(one_liner)
    one_liner =  one_liner
    return one_liner, detailed