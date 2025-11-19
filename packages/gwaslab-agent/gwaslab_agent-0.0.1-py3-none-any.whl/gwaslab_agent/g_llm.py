from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import json, os

GLOBAL_LLM = None

def get_llm(log, llm_configuration=None):
    log.write("Initiating connection to Large Language Model API...")
    if llm_configuration is None:
        key_path = os.path.expanduser("~/.gwaslab/LLM_KEY")
        with open(key_path, "r", encoding="utf-8") as f:
            llm_configuration = json.load(f)
    
    global GLOBAL_LLM
    
    if GLOBAL_LLM is None:
        provider = llm_configuration.get("provider", "openai")
        log.write(" -Connecting to Large Language Model API...")
        if provider == "openai":
            config = {k: v for k, v in llm_configuration.items() if k != "provider"}
            GLOBAL_LLM = ChatOpenAI(**config)
            log.write(" -Detected OpenAI-like API...")
        elif provider == "google":
            config = {k: v for k, v in llm_configuration.items() if k != "provider"}
            GLOBAL_LLM = ChatGoogleGenerativeAI(**config)
            log.write(" -Detected Google API...")
        elif provider == "azure":
            config = {k: v for k, v in llm_configuration.items() if k != "provider"}
            GLOBAL_LLM = AzureChatOpenAI(**config)
            log.write(" -Detected Azure OpenAI API...")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    model_name = (
        getattr(GLOBAL_LLM, "model", None)
        or getattr(GLOBAL_LLM, "model_name", None)
    )
    if model_name is not None:
        log.write(f" -Model used: {model_name}...")
    return GLOBAL_LLM
