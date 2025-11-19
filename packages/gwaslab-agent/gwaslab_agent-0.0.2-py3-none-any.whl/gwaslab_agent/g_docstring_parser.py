def parse_numpy_style_params(obj):
    """
    Parse NumPy-style docstrings with possibly multiple sections:
      summary, Parameters, Returns, summary, Parameters, Returns, ...

    Supported patterns:
        - Section headers with underline (e.g., "Parameters\\n----------")
        - Parameter lines with format: name : type [optional], description
        - Default values specified in type annotation or description
        - Enum detection from curly braces (e.g., {"case", "control"})
        - Type normalization to JSON-compatible types (string, number, array, object)
        - Multiple parameter sections merged into single output
        - Summary text collected from multiple locations

    Examples:
        >>> def example_func():
        ...     \"\"\"
        ...     Example function with parameters.
        ...
        ...     Parameters
        ...     ----------
        ...     x : int, default=10
        ...         Description of x with default.
        ...     y : {"low", "medium", "high"}
        ...         Description of y with enum.
        ...     z : array-like
        ...         Description of z with array type.
        ...     typo_example : float or stiring
        ...         Description showing how typos are handled as objects.
        ...     gtf_path : str, default='default'
        ...         Path to GTF file for gene annotation.
        ...         gtf_path options:
        ...         - 'default' : same as 'ensembl'.`build` should be specified.
        ...         - 'ensembl' : GTF from ensembl. `build` should be specified.
        ...         - 'refseq' : GTF from refseq. `build` should be specified.
        ...         - str : path for user provided gtf
        ...
        ...     Returns
        ...     -------
        ...     result : bool
        ...         Description of return value.
        ...     \"\"\"
        ...     pass

        >>> def multi_section_func():
        ...     \"\"\"
        ...     Function with multiple parameter sections.
        ...
        ...     Parameters
        ...     ----------
        ...     a : str
        ...         Description of a.
        ...
        ...     Less Used Parameters
        ...     --------------------
        ...     b : float or string, optional, default=None
        ...         Description of b with union type and default.
        ...
        ...     Parameters
        ...     ----------
        ...     c : int
        ...         Description of c (repeated section).
        ...     \"\"\"
        ...     pass

    Returns:
        {
          "description": "<combined summaries>",
          "parameters": {
              <name>: {
                 "type": <json-schema-ish type string>,
                 "default": <python value or None>,
                 "description": <str>,
                 "enum": [..]  # when detected
                 "required": <bool>
              },
              ...
          }
        }
    Only the *Parameters* sections are parsed for args (Returns are ignored).
    """
    import inspect, re, ast

    doc = inspect.getdoc(obj) or ""
    lines = doc.splitlines()

    # --- helpers --------------------------------------------------------------
    def is_section_header(idx, title):
        s = lines[idx].strip().rstrip(":").lower()
        if s != title.lower():
            return False
        if idx+1 < len(lines):
            underline = lines[idx+1].strip()
            if set(underline) == {"-"} and len(underline) >= 3:
                return 2
        return 1

    SECTION_NAMES = {"parameters", "less used parameters", "returns", "notes", "examples", "see also", "references"}

    main_parameters = {}
    parameters = {} 

    # Normalize a free-form type string into a JSON-ish simple type + enum
    def normalize_type_and_enum(type_text):
        # Handle enums like {"19", "38"} or {'a','b'}
        enum = None
        t = (type_text or "").strip()

        # Extract enum set literal inside braces
        m_enum = re.match(r"^\{\s*(.+?)\s*\}$", t)
        if m_enum:
            items = [x.strip() for x in m_enum.group(1).split(",")]
            # strip quotes if present
            enum = [re.sub(r"^([\"'])(.*)\1$", r"\2", x) for x in items]
            # choose base type: strings by convention
            return "string", enum

        # Split union like "tuple or list" / "str or bool"
        parts = [p.strip() for p in re.split(r"\bor\b|[|]", t)]
        # map primitives
        def map_one(p):
            p = p.lower()
            if "tuple" in p or "list" in p or "array" in p:
                return "array"
            if p in ("int", "int64", "integer"):
                return "integer"
            if p in ("float", "float64", "number", "double"):
                return "number"
            if p in ("bool", "boolean"):
                return "boolean"
            if p in ("str", "string"):
                return "string"
            if "dict" in p or "mapping" in p:
                return "object"
            # anything else → treat as object (e.g., pandas.DataFrame)
            return "object"

        mapped = {map_one(p) for p in parts if p}
        # Prefer array if any array present, else object if object present, else first
        if "array" in mapped:
            out = "array"
        elif "object" in mapped:
            out = "object"
        elif "number" in mapped and "integer" in mapped:
            out = "number"
        else:
            out = next(iter(mapped or {"string"}))
        return out, enum

    # Parse a default string into a Python value; convert tuple→list
    def parse_default(default_text):
        """
        Parse default values from docstrings and return **JSON-compatible** Python values.
        This ensures:
        - None -> null
        - True/False -> true/false
        - tuples -> lists
        - numeric strings -> numbers
        - everything else -> string
        """
        if default_text is None:
            return None

        s = default_text.strip()

        # Normalize common nil / boolean forms
        if s.lower() in ("none", "null"):
            return None
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False

        # Strip leading `default=` if present
        s = re.sub(r"^\s*default\s*=\s*", "", s, flags=re.IGNORECASE)

        # Remove trailing commas (e.g., "(1, 2, 3,)")
        s = s.rstrip(",")

        # Try safe literal evaluation
        try:
            val = ast.literal_eval(s)

            # Normalize tuples -> lists for strict JSON compatibility
            if isinstance(val, tuple):
                return list(val)

            # Everything from literal_eval is already JSON-friendly:
            # (dict, list, int, float, bool, None, str)
            return val

        except Exception:
            # If it's a quoted string, remove the quotes
            m = re.match(r"""^(['"])(.*)\1$""", s)
            if m:
                return m.group(2)

            # Otherwise return raw string as-is
            return s

    # Merge two param dicts (from different sections)
    def merge_param(base, incr):
        out = dict(base)
        # type / enum: prefer first non-empty, then keep base if already there
        if "type" not in out or out["type"] is None:
            out["type"] = incr.get("type")
        if "enum" not in out or not out.get("enum"):
            if incr.get("enum"):
                out["enum"] = incr["enum"]
        # default: prefer the first non-None default encountered
        if out.get("default") is None and incr.get("default") is not None:
            out["default"] = incr["default"]
        # description: concatenate
        d1 = (out.get("description") or "").strip()
        d2 = (incr.get("description") or "").strip()
        if d1 and d2:
            out["description"] = d1 + "\n" + d2
        elif d2:
            out["description"] = d2
        # required: recompute later based on default presence if not explicitly set
        return out

    # Collect all summaries (text outside/above Parameters)
    summaries = []
    parameters = {}

    i = 0
    n = len(lines)
    summaries = []

    def collect_until_section(start_idx):
        acc = []
        j = start_idx
        while j < n:
            s = lines[j].strip()
            if s.rstrip(":").lower() in SECTION_NAMES:
                break
            acc.append(lines[j])
            j += 1
        return "\n".join(acc).strip(), j

    first_summary, i = collect_until_section(0)
    if first_summary:
        summaries.append(first_summary)

    current_section_is_main = True  # default: first Parameters block is main

    while i < n:
        s = lines[i].strip()
        key = s.rstrip(":").lower()

        # MAIN PARAMETERS
        if key == "parameters":
            current_section_is_main = True
            skip = is_section_header(i, "Parameters")
            i += skip
            parse_section = True

        # LESS USED PARAMETERS
        elif key == "less used parameters":
            current_section_is_main = False
            skip = is_section_header(i, "Less Used Parameters")
            i += skip
            parse_section = True

        else:
            parse_section = False

        if parse_section:
            current = None
            buf = []

            header_re = re.compile(
                r"""^
                    (?P<name>[\w.\-]+)\s*
                    :\s*
                    (?P<rest>.+?)\s*$
                """, re.VERBOSE
            )
            
            def flush_param():
                nonlocal current, buf, parameters, main_parameters
                if not current:
                    buf = []
                    return

                entry = parameters.get(current, {
                    "type": None, "default": None, "description": "", "enum": None
                })

                desc = "\n".join([b.lstrip() for b in buf]).strip()
                # ------------------------------------------------------------------
                # NEW: Detect "Default is X" or "default = X" at end of description
                # ------------------------------------------------------------------
                # Matches cases like:
                #   "Default is True."
                #   "default = 0.5"
                #   "Default: (5,20)"
                #   "default is 'hg19'"
                #   "DEFAULT IS [1,2]"
                #
                # detect "Default is X" in description (your existing logic)
                m = re.search(r"\b[Dd]efault\s*(?:is|=|:)\s*([^\.\n]+)", desc)
                if m and entry.get("default") is None:
                    raw = m.group(1).strip()
                    try:
                        val = ast.literal_eval(raw)
                        if isinstance(val, tuple):
                            val = list(val)
                        entry["default"] = val
                    except Exception:
                        val = re.sub(r"""^(['"])(.*)\1$""", r"\2", raw)
                        entry["default"] = val
                    desc = re.sub(r"\b[Dd]efault\s*(?:is|=|:)\s*[^\.\n]+\.?", "", desc).rstrip()

                # Merge description in
                inc = {"description": desc}
                parameters[current] = merge_param(entry, inc)

                # also update main_parameters if this block is main
                if current_section_is_main:
                    mp = main_parameters.get(current, {"type": None, "default": None, "description": "", "enum": None})
                    main_parameters[current] = merge_param(mp, inc)

                buf = []

            # Consume block

            j = i
            while j < n:
                ss = lines[j].strip()
                if ss.rstrip(":").lower() in SECTION_NAMES:
                    break

                m = header_re.match(ss)
                if m:
                    flush_param()
                    pname = m.group("name")
                    rest = m.group("rest")

                    # Split rest by commas (but be careful with braces/quotes)
                    # We look for ", default=..." and also pick up 'optional/required'
                    # Keep a loose parse then refine.
                    default_text = None
                    ann = rest

                    # Pull default=... if present (greedy to end)
                    mdef = re.search(r",\s*default\s*=\s*(.+)$", ann, flags=re.IGNORECASE)
                    if mdef:
                        default_text = mdef.group(1).strip()
                        ann = ann[:mdef.start()].rstrip()

                    # Optional/required hints
                    opt_flag = None
                    if re.search(r"\boptional\b", ann, re.IGNORECASE):
                        opt_flag = "optional"
                        ann = re.sub(r"\boptional\b", "", ann, flags=re.IGNORECASE).strip(", ").strip()
                    if re.search(r"\brequired\b", ann, re.IGNORECASE):
                        opt_flag = "required"
                        ann = re.sub(r"\brequired\b", "", ann, flags=re.IGNORECASE).strip(", ").strip()

                    # Now 'ann' is the type annotation text
                    jtype, enum = normalize_type_and_enum(ann)

                    # Build current entry
                    entry = {
                        "type": jtype,
                        "default": parse_default(default_text),
                        "description": "",
                    }
                    if enum:
                        entry["enum"] = enum

                    if opt_flag == "required":
                        entry["required"] = True
                    elif opt_flag == "optional":
                        entry["required"] = False

                    # Normalize tuple default to list
                    if isinstance(entry.get("default"), tuple):
                        entry["default"] = list(entry["default"])

                    # If type implies array due to tuple/list word present in ann
                    if "tuple" in ann.lower() or "list" in ann.lower() or "array" in ann.lower():
                        entry["type"] = "array"

                    # merge into full parameters
                    if pname in parameters:
                        parameters[pname] = merge_param(parameters[pname], entry)
                    else:
                        parameters[pname] = entry

                    # merge into main parameters if this section is main
                    if current_section_is_main:
                        if pname in main_parameters:
                            main_parameters[pname] = merge_param(main_parameters[pname], entry)
                        else:
                            main_parameters[pname] = entry.copy()

                    current = pname
                    buf = []
                else:
                    buf.append(lines[j])
                j += 1

            flush_param()
            i = j
            continue

        # RETURNS or other sections: skip block, but also capture extra summaries
        if key in SECTION_NAMES:
            # skip the section (we don't need returns/others for args)
            skip = is_section_header(i, lines[i].strip().rstrip(":"))
            i += skip
            # Move to next section start
            while i < n:
                ss = lines[i].strip()
                if ss.rstrip(":").lower() in SECTION_NAMES:
                    break
                i += 1
            continue

        # Any loose text between sections counts as an additional summary
        extra_summary, i2 = collect_until_section(i)
        if extra_summary:
            summaries.append(extra_summary)
        i = i2

    # Post-process: set required if not explicitly set (no default => required)
    for k, v in list(parameters.items()):
        if "required" not in v:
            v["required"] = v.get("default") is None
        # ensure tuple-like defaults already converted to list
        if isinstance(v.get("default"), tuple):
            v["default"] = list(v["default"])
    
    parameters = {k: v for k, v in parameters.items() if k.lower() != "log"}
    main_parameters = {k: v for k, v in main_parameters.items() if k.lower() != "log"}

    combined_summary = "\n\n".join([s for s in summaries if s])
    
    ensure_items_for_arrays(parameters)
    ensure_items_for_arrays(main_parameters)
    #fix_array_items(parameters)
    #fix_array_items(main_parameters)


    return {
        "description": combined_summary.strip(),
        "parameters": parameters,       # full param dictionary
        "main_parameters": main_parameters  # only main section parameters
    }


def ensure_items_for_arrays(params):
    for k, v in params.items():
        if v.get("type") != "array":
            continue

        # If items already exists, skip
        if "items" in v:
            continue

        # Enum → array of enums
        if v.get("enum"):
            v["items"] = {"type": "string", "enum": v["enum"]}
            continue

        # Default-based inference
        d = v.get("default")
        if isinstance(d, list) and d:
            elem = d[0]
            if isinstance(elem, bool):
                t = "boolean"
            elif isinstance(elem, int):
                t = "integer"
            elif isinstance(elem, float):
                t = "number"
            elif isinstance(elem, dict):
                t = "object"
            else:
                t = "string"
            v["items"] = {"type": t}
            continue

        # Fallback safe
        v["items"] = {"type": "string"}

    for k, v in params.items():
        if v.get("type") == "object":
            # Azure requires additionalProperties or properties
            if "properties" not in v and "additionalProperties" not in v:
                v["additionalProperties"] = {"type": "string"}  

def fix_array_items(schema: dict):
    """
    Ensure every array type in schema has 'items'. Azure will error otherwise.
    Apply recursively.
    """
    if not isinstance(schema, dict):
        return

    if schema.get("type") == "array":
        if "items" not in schema:
            # safe fallback
            schema["items"] = {"type": "string"}

    # Deep fix for nested objects
    for key, value in schema.items():
        if isinstance(value, dict):
            fix_array_items(value)
        elif isinstance(value, list):
            for v in value:
                fix_array_items(v)