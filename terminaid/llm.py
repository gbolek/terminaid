import requests
import json
import base64
from .config import get_ollama_url, get_user_token, load_config

def get_system_prompt():
    """Return the system prompt for the LLM."""
    return """You are TerminAid, a specialized assistant focused on providing terminal commands.

Your response must follow this exact format:
1. First line: Either "SAFE" or "DANGEROUS" based on your assessment of the command's potential risk
2. Second line: If "DANGEROUS", provide a brief explanation of the risks (one line only)
3. Third line: The exact terminal command that accomplishes the task

Classify a command as DANGEROUS if it:
- Deletes or modifies files or directories without confirmation
- Makes irreversible changes to the system
- Could harm system stability or functionality
- Irreversibly removes information from git repositories
- Modifies critical system files or settings
- Has high potential for data loss if used incorrectly
- Uses sudo or root privileges for potentially harmful operations
- Runs scripts or code from the internet without inspection
- Could affect network security

Example response for a safe command:
SAFE
ls -la

Example response for a dangerous command:
DANGEROUS
This command will permanently delete files without confirmation
rm -rf ./some_directory

Do not include any explanations, markdown formatting, or text other than what is specified above.
If multiple commands are needed, combine them with && or provide a short script with proper line breaks.
If you're unsure, provide the most likely command that would work in a standard macOS environment."""

def query_llm(user_query):
    """Query the LLM with the user's request and return the response."""
    config = load_config()
    model = config.get("model")
    ollama_url = get_ollama_url()
    user_token = get_user_token()
    
    headers = {"Content-Type": "application/json"}
    if user_token:
        # Use Basic authentication
        headers["Authorization"] = f"Basic {user_token}"
    
    data = {
        "model": model,
        "prompt": user_query,
        "system": get_system_prompt(),
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        result = response.json()
        return parse_llm_response(result.get("response", "").strip())
    except requests.exceptions.RequestException as e:
        return {"is_dangerous": False, "warning": "", "command": f"Error connecting to Ollama server: {str(e)}"}

def parse_llm_response(response):
    """Parse the LLM response to extract safety information and command."""
    lines = response.strip().split('\n')
    
    result = {
        "is_dangerous": False,
        "warning": "",
        "command": ""
    }
    
    if not lines:
        return result
    
    # First line should be SAFE or DANGEROUS
    if lines[0].upper() == "DANGEROUS":
        result["is_dangerous"] = True
        
        # Second line should be the warning if dangerous
        if len(lines) > 1:
            result["warning"] = lines[1]
            
        # Command starts from the third line
        if len(lines) > 2:
            result["command"] = '\n'.join(lines[2:])
    else:
        # If SAFE or any other response, the command starts from the second line
        if len(lines) > 1:
            result["command"] = '\n'.join(lines[1:])
        else:
            result["command"] = lines[0]  # Fallback if only one line
    
    return result
