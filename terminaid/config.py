import json
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "model": "llama2",
    "ollama_url": "http://localhost:11434",
    "user_token": ""
}

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "terminaid"
CONFIG_FILE = CONFIG_DIR / "config.json"

def ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """Load configuration from file, creating default if it doesn't exist."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            
        # Ensure all required keys exist
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                
        return config
    except (json.JSONDecodeError, IOError):
        # If the file is corrupted or can't be read, use defaults
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_ollama_url():
    """Get Ollama server URL from config."""
    config = load_config()
    return config.get("ollama_url", DEFAULT_CONFIG["ollama_url"])

def get_user_token():
    """Get user token from config."""
    config = load_config()
    return config.get("user_token", DEFAULT_CONFIG["user_token"])

def set_model(model_name):
    """Set the model to use for queries."""
    config = load_config()
    config["model"] = model_name
    save_config(config)
    return config

def set_ollama_url(url):
    """Set the Ollama server URL."""
    config = load_config()
    config["ollama_url"] = url
    save_config(config)
    return config

def set_user_token(token):
    """Set the user token."""
    config = load_config()
    config["user_token"] = token
    save_config(config)
    return config
