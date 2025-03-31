import sys
import argparse
import pyperclip
import os
import readline
import shlex
from .llm import query_llm
from .config import (
    set_model, 
    set_ollama_url, 
    set_user_token, 
    load_config
)

def execute_command(response):
    """Set up the command for execution with cursor at the end."""
    command = response["command"]
    
    # Display warning if dangerous
    if response["is_dangerous"]:
        print("\033[91m⚠️  WARNING - POTENTIALLY DANGEROUS OPERATION ⚠️\033[0m")
        print(f"\033[91m{response['warning']}\033[0m")
        print()
    
    # Set up the command for execution with cursor at the end
    readline.set_startup_hook(lambda: readline.insert_text(command))
    try:
        # No extra confirmation for dangerous commands, just the standard prompt
        input("Terminaid: ")
        
        # If confirmed, execute the command
        os.system(command)
    except KeyboardInterrupt:
        print("\nCommand execution cancelled.")
    finally:
        # Reset the startup hook
        readline.set_startup_hook()

def query_handler(query, copy=False, print_only=False):
    """Handle a user query."""
    response = query_llm(query)
    
    if copy:
        try:
            command = response["command"]
            pyperclip.copy(command)
            
            # Display warning if dangerous
            if response["is_dangerous"]:
                print("\033[91m⚠️  WARNING - POTENTIALLY DANGEROUS OPERATION ⚠️\033[0m")
                print(f"\033[91m{response['warning']}\033[0m")
                print()
            
            print(command)
            print("\n(Command copied to clipboard)")
        except Exception:
            print(response["command"])
            print("\n(Failed to copy to clipboard)")
    elif print_only:
        # Just print the command without execution prompt
        # But still show warning if dangerous
        if response["is_dangerous"]:
            print("\033[91m⚠️  WARNING - POTENTIALLY DANGEROUS OPERATION ⚠️\033[0m")
            print(f"\033[91m{response['warning']}\033[0m")
            print()
        
        print(response["command"])
    else:
        # Default behavior: execute mode
        execute_command(response)

def set_handler(parameter, value):
    """Handle the 'set' command."""
    if parameter == "model":
        config = set_model(value)
        print(f"Model set to: {config['model']}")
    elif parameter == "url":
        config = set_ollama_url(value)
        print(f"Ollama URL set to: {config['ollama_url']}")
    elif parameter == "token":
        config = set_user_token(value)
        print(f"User token updated")
    else:
        print(f"Unknown parameter: {parameter}")
        print("Available parameters: model, url, token")

def config_handler():
    """Handle the 'config' command."""
    config = load_config()
    
    # Hide token in display for security
    display_config = config.copy()
    if display_config.get("user_token"):
        display_config["user_token"] = "********" 
    
    print("Current configuration:")
    for key, value in display_config.items():
        print(f"  {key}: {value}")

def show_help():
    """Show help information."""
    config = load_config()
    print(f"Current model: {config['model']}")
    print("Usage examples:")
    print("  terminaid \"how to list all files including hidden ones\"")
    print("  terminaid -p \"how to list all files including hidden ones\"")
    print("  terminaid -c \"how to list all files including hidden ones\"")
    print("  terminaid set model llama2")
    print("  terminaid config")
    print("\nOptions:")
    print("  -c, --copy       Copy command to clipboard")
    print("  -p, --print-only Print command only without execution prompt")
    print("  -h, --help       Show this help message")
    print("\nSafety Features:")
    print("  - Commands that could be dangerous will display a warning")
    print("  - Clear visual indicators for risky commands")

def main():
    """Main entry point for the CLI."""
    # Show help if no arguments
    if len(sys.argv) == 1:
        show_help()
        return
    
    # Check for explicit commands first
    if sys.argv[1] == "config":
        config_handler()
        return
    
    if sys.argv[1] == "set" and len(sys.argv) >= 4:
        parameter = sys.argv[2]
        value = sys.argv[3]
        set_handler(parameter, value)
        return
    
    # Parse options for query mode
    copy_flag = False
    print_only_flag = False
    query_parts = []
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ["-c", "--copy"]:
            copy_flag = True
            i += 1
        elif arg in ["-p", "--print-only"]:
            print_only_flag = True
            i += 1
        elif arg in ["-h", "--help"]:
            show_help()
            return
        else:
            # Everything else is part of the query
            query_parts.append(arg)
            i += 1
    
    # If we have a query, process it
    if query_parts:
        query = " ".join(query_parts)
        query_handler(query, copy_flag, print_only_flag)
    else:
        show_help()

if __name__ == "__main__":
    main()
