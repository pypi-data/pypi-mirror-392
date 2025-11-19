
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


def print_message(self, console, msg, step, return_message, verbose, verbose_return, if_print=False, title = "AGENT"):
    invalid_calls = getattr(msg, "invalid_tool_calls", [])
    if invalid_calls:
        for ic in invalid_calls:
            name = ic.get("name", "unknown_tool")
            args = ic.get("args")
            error = ic.get("error", "Unknown error")

            console.rule("[bold red]INVALID TOOL CALL[/bold red]")
            console.print(f"[bold yellow]Tool:[/bold yellow] {name}")
            console.print(f"[bold yellow]Args (raw):[/bold yellow] {args}")
            console.print(f"[bold red]Error:[/bold red] {error}")

            # Log it
            self.log.write(f"[INVALID_TOOL_CALL] {name} args={args}")
            self.log.write(f"[ERROR] {error}")
            
        # Skip further handling of this message
        return None

    refusal = getattr(msg, "additional_kwargs", {}).get("refusal")
    if refusal:
        console.rule("[bold red]MODEL REFUSAL[/bold red]")
        console.print(Markdown(refusal))
        self.log.write(f"[ERROR] Model refusal: {refusal}")
        return None

    error = getattr(msg, "response_metadata", {}).get("error")
    if error:
        console.rule("[bold red]MODEL ERROR[/bold red]")
        console.print(Text(str(error), style="red"))
        self.log.write(f"[ERROR] Model error: {error}")
        return None
    
    # --- Tool call(s) ---
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        for call in msg.tool_calls:
            name = call.get("name", "unknown_tool")
            args = call.get("args", {})
            self.log.write(f"[TOOL] {name}({args})")
            self._add_toolcalls(f"{name}({args})")

        # --- Usage per tool call step ---
        usage = getattr(msg, "response_metadata", {}).get("token_usage") \
            or getattr(msg, "usage_metadata", None)
        if usage:
            prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
            completion = usage.get("completion_tokens", usage.get("output_tokens"))
            total = usage.get("total_tokens")
            self.log.write(f" [USAGE] prompt={prompt}, completion={completion}, total={total}",verbose=verbose)

    # --- Text output ---
    elif getattr(msg, "content", None):
        if step=="tools":
            self.log.write(f"[TOOL RETURN] {msg.content}",verbose=verbose&verbose_return)
        else:
            #self.log.write(f"[bold green]{step.upper()} OUTPUT[/bold green]")
            #self.log.write(Markdown(msg.content))

            if return_message==True:
                if if_print:
                    console.rule(f"[bold]GWASLAB {title} OUTPUT[/bold]", style="rule.text")
                    console.print(Panel(Markdown(ensure_string(msg.content))))
                return msg.content
            else:
                console.rule(f"[bold]GWASLAB {title} OUTPUT[/bold]", style="rule.text")
                console.print(Panel(Markdown(ensure_string(msg.content))))

        # --- Usage per text step ---
        usage = getattr(msg, "response_metadata", {}).get("token_usage") \
            or getattr(msg, "usage_metadata", None)
        if usage:
            prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
            completion = usage.get("completion_tokens", usage.get("output_tokens"))
            total = usage.get("total_tokens")
            self.log.write(f" [USAGE] prompt={prompt}, completion={completion}, total={total}",verbose=verbose)
    return None

def ensure_string(x):
    """Convert msg.content to a safe string in ALL cases."""
    if x is None:
        return ""

    # If already a string
    if isinstance(x, str):
        return x

    # If bytes or bytearray
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", errors="replace")

    # If list (could be tokens, dicts, or full tool outputs)
    if isinstance(x, list):
        parts = []
        for item in x:
            #  handle list of dicts with "text"
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "".join(parts)

    # If dict (JSON-like message)
    if isinstance(x, dict):
        #  Extract "text" when present
        if "text" in x and isinstance(x["text"], str):
            return x["text"]

        # Otherwise return JSON string
        import json
        try:
            return json.dumps(x, ensure_ascii=False)
        except Exception:
            return str(x)

    # Fallback for all other types (ints, floats, objects, etc.)
    return str(x)
