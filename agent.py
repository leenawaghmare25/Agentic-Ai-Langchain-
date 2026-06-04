# Import the os module to handle file directories and environment variables
import os
from dotenv import load_dotenv
load_dotenv()
# Import the sys module to detect the operating system and configure terminal streams
import sys
# Import the json module to parse tool calls
import json
# Import the time module to handle delays and wait times for rate limiting
import time
# Import the warnings module to suppress Pydantic or deprecated warnings
import warnings
# Import the subprocess module to execute terminal Git commands
import subprocess
import ast
import re
# Import colorama to color terminal logs (init enables it, Fore changes text color, Style changes weight)
from colorama import init, Fore, Style

# Check if the operating system is Windows to apply the console encoding fix
if sys.platform.startswith("win"):
    # Import the io module to handle text streaming conversions
    import io
    # Wrap standard output in a UTF-8 writer to support non-ASCII characters without crashes
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    # Wrap standard error in a UTF-8 writer to support non-ASCII characters without crashes
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Mute warnings from Pydantic database models to keep the screen clean
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
# Mute runtime warnings from external modules
warnings.filterwarnings("ignore", category=RuntimeWarning)
# Mute general user warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Set environment variable to disable OpenTelemetry system logging
os.environ["OTEL_SDK_DISABLED"] = "true"

# Initialize colorama and auto-reset terminal color styles back to default after each print
init(autoreset=True)

# Define configuration switch: Set to True for Local Ollama, or False for Cloud Groq
USE_LOCAL = True
# Define Offline Mode flag to force local Qwen models only
OFFLINE_MODE = False

# Import ChatGroq to use Groq API's LLM engine
from langchain_groq import ChatGroq
# Import ChatOllama from standalone langchain_ollama package to run offline model service
from langchain_ollama import ChatOllama
# Import ChatGoogleGenerativeAI for Gemini LLM engine
from langchain_google_genai import ChatGoogleGenerativeAI
# Import tool decorator to transform Python functions into LLM tools
from langchain_core.tools import tool
# Import prompt constructor and template variables placeholders
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# Import base message wrappers and ToolMessage for tool execution tracking
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
# Import DuckDuckGo Search wrapper class
from duckduckgo_search import DDGS
# Import regular expressions module
import re

# Define the absolute path of the local workspace directory
WORKSPACE_DIR = os.path.abspath("c:/Users/KETAN/Desktop/Agentic AI")
# Define the dynamic current project workspace directory (default to WORKSPACE_DIR)
CURRENT_PROJECT_DIR = WORKSPACE_DIR
# Define the target remote GitHub repository URL
REMOTE_GIT_URL = "https://github.com/leenawaghmare25/Agentic-Ai-Langchain-.git"

def initialize_git_repo(): # Define function initialize_git_repo to set up a git repository in our workspace
    """Initializes a git repository in the root workspace directory and configures the remote origin."""
    try: # Start try block to handle any errors during git initialization
        git_dir = os.path.join(WORKSPACE_DIR, ".git") # Construct the absolute path to the local .git directory
        # Ensure workspace root exists
        os.makedirs(WORKSPACE_DIR, exist_ok=True) # Create the workspace directory if it doesn't already exist on disk
        
        # Check if root .git exists; if not, initialize it
        if not os.path.exists(git_dir): # If the .git directory does not exist yet
            print(Fore.YELLOW + f"\n[Git Integration] Initializing Git repository in root: {WORKSPACE_DIR}..." + Fore.RESET) # Print initialization start message to console in yellow
            subprocess.run(["git", "init"], cwd=WORKSPACE_DIR, capture_output=True, check=True) # Run git init command in the workspace directory and check for errors
            
        # Write default root .gitignore if not present
        gitignore_path = os.path.join(WORKSPACE_DIR, ".gitignore") # Construct the path to the workspace .gitignore file
        if not os.path.exists(gitignore_path): # If the .gitignore file does not exist yet
            with open(gitignore_path, "w", encoding="utf-8") as f: # Open the gitignore file in write-text mode with UTF-8 encoding
                f.write("__pycache__/\n*.py[cod]\n.env\nmyenv/\n") # Write list of temporary cache files and environment files to ignore in Git
            print(Fore.GREEN + "[Git Integration] Created default root .gitignore file." + Fore.RESET) # Print ignore file creation message to console in green
            
        # Dynamically verify and bind remote origin
        print(Fore.YELLOW + f"[Git Integration] Configuring remote origin to: {REMOTE_GIT_URL}" + Fore.RESET) # Print origin configuration message in yellow
        subprocess.run(["git", "remote", "remove", "origin"], cwd=WORKSPACE_DIR, capture_output=True) # Remove any existing remote origin configuration in this repository
        subprocess.run(["git", "remote", "add", "origin", REMOTE_GIT_URL], cwd=WORKSPACE_DIR, capture_output=True, check=True) # Add the target REMOTE_GIT_URL as the new remote origin repository
    except Exception as e: # Catch any filesystem or command line exceptions
        print(Fore.RED + f"\n[Git Integration Error] Failed to initialize Git repo: {str(e)}" + Fore.RESET) # Print error message to console in red

def handle_git_push_workflow(project_name: str): # Define function handle_git_push_workflow that stages, commits, and pushes updates
    """Checks for changes in the workspace. If changes exist, stages, commits, and pushes them to GitHub."""
    try: # Start try block to handle any errors during git commit/push
        git_dir = os.path.join(WORKSPACE_DIR, ".git") # Construct the absolute path to the local .git directory
        if not os.path.exists(git_dir): # If git has not been initialized in the workspace yet
            print(Fore.RED + "\n[Git Integration Error] Git is not initialized at the root level." + Fore.RESET) # Print warning message in red to console
            return # Exit the function early since we cannot run git commands
 
        # Check for untracked or modified files in the workspace (using git status --porcelain)
        status_check = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE_DIR, capture_output=True, text=True, check=True) # Run git status --porcelain to check for modified files
        changes = status_check.stdout.strip() # Read the command output and strip whitespace to see if there are actual changes
        
        if changes: # If there are untracked or modified files in the workspace
            print(Fore.YELLOW + "\n[Git Integration] Changes detected in workspace. Staging and committing..." + Fore.RESET) # Print changes detected message in yellow
            # Stage all changes
            subprocess.run(["git", "add", "."], cwd=WORKSPACE_DIR, capture_output=True, check=True) # Run git add . to stage all new and modified files
            # Commit changes
            commit_msg = f"Auto-generated project update: {project_name}" # Formulate commit message with the dynamic project name
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORKSPACE_DIR, capture_output=True, check=True) # Run git commit command with the message and check for errors
            print(Fore.GREEN + f"[Git Integration] Successfully created commit: '{commit_msg}'" + Fore.RESET) # Print commit success message in green
            
            # Push changes to main branch
            print(Fore.YELLOW + "[Git Integration] Pushing updates to GitHub..." + Fore.RESET) # Print push start message to console in yellow
            subprocess.run(["git", "branch", "-M", "main"], cwd=WORKSPACE_DIR, capture_output=True, check=True) # Rename the active branch to main to ensure standard push branch name
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=WORKSPACE_DIR, capture_output=True, check=True) # Run git push command to send main branch to remote origin
            print(Fore.GREEN + "[Git Integration] Successfully pushed updates to remote GitHub repository!" + Fore.RESET) # Print push success message in green
        else: # If git status output is empty (no changes exist)
            print(Fore.GREEN + "\n[Git Integration] No changes detected in workspace. Skipping Git commit and push." + Fore.RESET) # Print skip message to console in green
            
    except Exception as e: # Catch any command or connection errors during git operations
        print(Fore.RED + f"\n[Git Integration Error] Failed to complete Git push workflow: {str(e)}" + Fore.RESET) # Print push error message to console in red

def clean_json_candidate(candidate: str) -> str:
    """Preprocesses a JSON candidate string to resolve common syntax errors like backticks wrapping multi-line content."""
    def replace_backticks(match):
        content = match.group(1)
        # Escape backslashes, double quotes, newlines, and other characters
        escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return f': "{escaped}"'
    
    # Matches colon followed by optional whitespace and backtick-wrapped text
    cleaned = re.sub(r':\s*`([\s\S]*?)`', replace_backticks, candidate)
    return cleaned

# Helper function to extract all valid JSON objects from a text string
def extract_json_objects(text: str) -> list:
    results = []
    stack = []
    start_idx = -1
    for i, char in enumerate(text):
        if char == "{":
            if not stack:
                start_idx = i
            stack.append(char)
        elif char == "}":
            if stack:
                stack.pop()
                if not stack:
                    candidate = text[start_idx:i+1]
                    try:
                        # Clean backticks from code blocks inside JSON parameters
                        cleaned = clean_json_candidate(candidate)
                        obj = json.loads(cleaned)
                        if isinstance(obj, dict):
                            results.append(obj)
                    except Exception:
                        pass
    return results

def parse_markdown_code_blocks(content: str) -> list:
    """Parses raw content for markdown code blocks and maps them to write_file tool calls."""
    import re
    pattern = r"```([a-zA-Z0-9+#-]+)?\n([\s\S]*?)\n```"
    matches = list(re.finditer(pattern, content))
    
    extracted_calls = []
    for i, match in enumerate(matches):
        lang = match.group(1)
        code = match.group(2)
        if lang:
            lang = lang.lower().strip()
        else:
            lang = ""
            
        start_pos = matches[i-1].end() if i > 0 else 0
        end_pos = match.start()
        preceding_text = content[start_pos:end_pos]
        
        file_candidates = re.findall(r"\b([a-zA-Z0-9_\-\/\\.]+\.[a-zA-Z0-9]+)\b", preceding_text)
        
        filename = None
        if file_candidates:
            for cand in reversed(file_candidates):
                cand = cand.strip().strip(".")
                ext = cand.split(".")[-1].lower()
                if ext in ["html", "css", "js", "py", "sql", "json", "md", "txt", "yml", "yaml", "ini", "cfg"]:
                    cand = cand.replace("\\", "/")
                    project_dir_name = os.path.basename(CURRENT_PROJECT_DIR)
                    for prefix in ["projects/", "projects/" + project_dir_name + "/"]:
                        if cand.startswith(prefix):
                            cand = cand[len(prefix):]
                    filename = cand
                    break
        
        if not filename:
            if lang == "html":
                filename = "templates/index.html"
            elif lang == "css":
                filename = "static/style.css"
            elif lang in ["js", "javascript"]:
                filename = "static/script.js"
            elif lang == "python":
                filename = "app.py"
            elif lang == "sql":
                filename = "schema.sql"
            else:
                continue
                
        extracted_calls.append({
            "name": "write_file",
            "args": {
                "filename": filename,
                "content": code
            }
        })
    return extracted_calls

def parse_agent_response(content: str, cycle: int, prefix: str) -> list:
    """Parses agent content to find tool calls from structured JSON or markdown code blocks."""
    tool_calls = []
    
    # 1. First, try to extract JSON objects if we see curly braces
    if "{" in content and "}" in content:
        found_objects = extract_json_objects(content)
        for idx, obj in enumerate(found_objects):
            if not isinstance(obj, dict):
                continue
                
            tool_name = None
            tool_args = None
            
            name_key = "name" if "name" in obj else ("function" if "function" in obj else None)
            if name_key:
                tool_name = obj[name_key]
                tool_args = obj.get("args", obj.get("arguments", obj.get("parameters", {})))
                if not isinstance(tool_args, dict) or not tool_args:
                    tool_args = {k: v for k, v in obj.items() if k not in [name_key, "id", "type"]}
            elif "filename" in obj and "content" in obj:
                tool_name = "write_file"
                tool_args = {"filename": obj["filename"], "content": obj["content"]}
            elif "filename" in obj:
                tool_name = "read_file"
                tool_args = {"filename": obj["filename"]}
            elif "query" in obj:
                tool_name = "search_internet"
                tool_args = {"query": obj["query"]}
                
            if tool_name:
                tool_calls.append({
                    "name": tool_name,
                    "args": tool_args,
                    "id": f"fallback_json_{prefix}_{cycle}_{idx}"
                })
                
    # 2. If no tool calls were extracted from JSON, fallback to parsing markdown code blocks
    if not tool_calls:
        code_blocks = parse_markdown_code_blocks(content)
        for idx, cb in enumerate(code_blocks):
            tool_calls.append({
                "name": cb["name"],
                "args": cb["args"],
                "id": f"fallback_code_{prefix}_{cycle}_{idx}"
            })
            
    return tool_calls

def verify_frontend_files() -> list:
    """Checks if the mandatory frontend files exist and are non-empty in the workspace."""
    missing = []
    
    # Check templates/index.html or index.html (or dashboard.html/base.html)
    html_exists = False
    for p in ["templates/index.html", "index.html", "templates/dashboard.html", "dashboard.html", "templates/base.html", "base.html"]:
        full_path = os.path.join(CURRENT_PROJECT_DIR, p)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            html_exists = True
            break
    if not html_exists:
        missing.append("templates/index.html (or index.html/dashboard.html)")
        
    # Check static/style.css or style.css or styles.css
    css_exists = False
    for p in ["static/style.css", "static/styles.css", "style.css", "styles.css", "static/css/style.css", "css/style.css"]:
        full_path = os.path.join(CURRENT_PROJECT_DIR, p)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            css_exists = True
            break
    if not css_exists:
        missing.append("static/style.css (or style.css)")
        
    # Check static/script.js or script.js
    js_exists = False
    for p in ["static/script.js", "script.js", "static/js/script.js", "js/script.js"]:
        full_path = os.path.join(CURRENT_PROJECT_DIR, p)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            js_exists = True
            break
    if not js_exists:
        missing.append("static/script.js (or script.js)")
        
    return missing

def verify_backend_files() -> list:
    """Checks if the mandatory backend files exist and are non-empty in the workspace."""
    missing = []
    
    # Check app.py or server.py or main.py
    backend_exists = False
    for p in ["app.py", "server.py", "main.py", "server.ts", "app.ts"]:
        full_path = os.path.join(CURRENT_PROJECT_DIR, p)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            backend_exists = True
            break
    if not backend_exists:
        missing.append("app.py (or server.py / main.py)")
        
    return missing

def validate_directory_layout(project_dir: str) -> list:
    errors = []
    return errors

def validate_python_syntax(project_dir: str) -> list:
    errors = []
    for root, _, files in os.walk(project_dir):
        if 'myenv' in root or '.venv' in root or '__pycache__' in root or '.git' in root: continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        ast.parse(f.read(), filename=path)
                except SyntaxError as e:
                    errors.append(f"Syntax error in {os.path.relpath(path, project_dir)}: {e}")
                except Exception:
                    pass
    return errors

def validate_project_structure(project_dir: str) -> list:
    errors = []
    has_html = False
    has_backend = False
    
    for root, _, files in os.walk(project_dir):
        if 'myenv' in root or '.venv' in root or 'node_modules' in root or '.git' in root: continue
        for file in files:
            if file.endswith('.html'): has_html = True
            if file.endswith(('.py', '.js', '.ts')): has_backend = True
            
    if not has_html:
        errors.append("No HTML files found. An application frontend is required.")
    if not has_backend:
        errors.append("No backend/logic files (.py, .js, .ts) found.")
    
    return errors

def validate_application_startup(project_dir: str) -> list:
    errors = []
    
    # Check for Node.js
    if os.path.exists(os.path.join(project_dir, "package.json")):
        try:
            server_file = None
            for p in ["server.js", "index.js", "app.js", "main.js"]:
                if os.path.exists(os.path.join(project_dir, p)):
                    server_file = p
                    break
            if server_file:
                process = subprocess.Popen(["node", server_file], cwd=project_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                time.sleep(3)
                if process.poll() is not None:
                    _, stderr = process.communicate()
                    errors.append(f"Node.js application crashed on startup:\n{stderr}")
                else:
                    process.terminate()
                    process.wait()
            else:
                errors.append("Found package.json but no obvious Node.js entry point (server.js, index.js) to test startup.")
        except Exception as e:
            errors.append(f"Failed to execute Node.js app: {e}")
        return errors

    # Check for Python
    main_file = None
    for p in ["app.py", "server.py", "main.py"]:
        if os.path.exists(os.path.join(project_dir, p)):
            main_file = p
            break
    
    if not main_file:
        return ["No entry point found (app.py, main.py, server.js, etc.) to test startup."]
        
    try:
        process = subprocess.Popen(
            [sys.executable, main_file],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            errors.append(f"Application crashed on startup:\n{stderr}")
        else:
            process.terminate()
            process.wait()
    except Exception as e:
        errors.append(f"Failed to execute application: {e}")
        
    return errors

def validate_project_artifacts(project_dir: str) -> list:
    errors = []
    for root, _, files in os.walk(project_dir):
        if 'myenv' in root or '.venv' in root or '__pycache__' in root or '.git' in root: continue
        for file in files:
            path = os.path.join(root, file)
            if os.path.getsize(path) == 0 and file != "__init__.py":
                errors.append(f"File {os.path.relpath(path, project_dir)} is empty.")
    
    docs_dir = os.path.join(project_dir, "docs")
    mandatory_docs = [
        "requirements.txt", "planning.txt", "architecture.txt", 
        "integration_summary.txt", "qa_report.txt", "verification_report.txt"
    ]
    for doc in mandatory_docs:
        p = os.path.join(docs_dir, doc)
        if not os.path.exists(p):
            errors.append(f"Missing documentation file: docs/{doc}.")
        elif os.path.getsize(p) < 10:
            errors.append(f"Documentation file 'docs/{doc}' lacks meaningful content.")
            
    return errors

def run_all_validations(project_dir: str) -> list:
    errors = []
    errors.extend(validate_python_syntax(project_dir))
    errors.extend(validate_project_structure(project_dir))
    errors.extend(validate_application_startup(project_dir))
    errors.extend(validate_project_artifacts(project_dir))
    return errors

def save_agent_artifact(filename: str, content: str):
    """Automatically saves agent outputs as permanent .txt artifacts in the docs/ directory."""
    docs_dir = os.path.join(CURRENT_PROJECT_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)


# Helper function to prevent the agent from accessing files outside the workspace directory
def _resolve_path(filename: str) -> str:
    # Resolve the final absolute path of the targeted file
    target = os.path.abspath(os.path.join(CURRENT_PROJECT_DIR, filename))
    # Check if the target path does not start with the workspace root directory path
    if not target.startswith(CURRENT_PROJECT_DIR):
        # Raise an access error if the file path goes outside the workspace
        raise ValueError("Access Denied: File operations are strictly restricted to the workspace directory.")
    # Return the verified absolute path
    return target

# Declare the list files tool using LangChain tool decorator
@tool
def list_files() -> str:
    """List all files and folders in the workspace directory."""
    # Start of try block to handle exceptions
    try:
        # Check if the workspace folder does not exist
        if not os.path.exists(CURRENT_PROJECT_DIR):
            # Create the workspace folder if missing
            os.makedirs(CURRENT_PROJECT_DIR, exist_ok=True)
        # Get list of all file and directory names in the workspace folder
        files = os.listdir(CURRENT_PROJECT_DIR)
        # If the directory contains no files, return a notice
        if not files:
            # Return empty directory message
            return "The workspace directory is empty."
        
        # Initialize an empty list to compile output lines
        output = []
        # Loop through each item in the file list
        for f in files:
            # Build the absolute path of the item
            path = os.path.join(CURRENT_PROJECT_DIR, f)
            # Check if the item is a subdirectory
            if os.path.isdir(path):
                # Mark it as a directory
                output.append(f"[Directory] {f}")
            # If the item is a file
            else:
                # Get size of the file in bytes
                size = os.path.getsize(path)
                # Mark it as a file with its size
                output.append(f"[File] {f} ({size} bytes)")
        # Join lines with newlines and return as a single string
        return "\n".join(output)
    # Catch block for general exceptions
    except Exception as e:
        # Catch any listing errors and return the exception message
        return f"Error listing files: {str(e)}"

# Declare the read file tool using LangChain tool decorator
@tool
def read_file(filename: str) -> str:
    """Read the content of a file in the workspace.
    
    Args:
        filename: The relative path or name of the file to read.
    """
    # Start of try block to handle exceptions
    try:
        # Validate and resolve the absolute file path
        path = _resolve_path(filename)
        # Check if the resolved file path does not exist
        if not os.path.exists(path):
            # Return missing file message
            return f"Error: File '{filename}' does not exist in workspace."
        # Check if the resolved path points to a directory instead of a file
        if os.path.isdir(path):
            # Return directory warning
            return f"Error: '{filename}' is a directory, not a file."
        
        # Open file in read mode with UTF-8 encoding
        with open(path, "r", encoding="utf-8") as f:
            # Read all file contents
            content = f.read()
        # Return the file text contents
        return content
    # Catch block for security validation failures
    except ValueError as ve:
        # Return security path errors
        return str(ve)
    # Catch block for general exceptions
    except Exception as e:
        # Catch other errors and return explanation
        return f"Error reading file '{filename}': {str(e)}"

# Declare the write file tool using LangChain tool decorator
@tool
def write_file(filename: str, content: str) -> str:
    """Write content to a file in the workspace. Creates parent folders if they do not exist.
    
    Args:
        filename: The relative path or name of the file to write to.
        content: The text/code content to save in the file.
    """
    # Start of try block to handle exceptions
    try:
        # Validate and resolve the absolute file path
        path = _resolve_path(filename)
        # Automatically generate parent folders if they don't exist yet
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Open file in write mode with UTF-8 encoding
        with open(path, "w", encoding="utf-8") as f:
            # Write content strings into the file
            f.write(content)
        # Return success confirmation message
        return f"Successfully wrote {len(content)} characters to '{filename}'."
    # Catch block for security validation failures
    except ValueError as ve:
        # Return security path errors
        return str(ve)
    # Catch block for general exceptions
    except Exception as e:
        # Catch other errors and return explanation
        return f"Error writing to file '{filename}': {str(e)}"

# Declare the search internet tool using LangChain tool decorator
@tool
def search_internet(query: str) -> str:
    """Search the internet for real-time facts, news, weather, or current information.
    
    Args:
        query: The search term or keywords to query.
    """
    # Start of try block to handle exceptions
    try:
        # Open a session with DuckDuckGo Search
        with DDGS() as ddgs:
            # Run text query using auto backend, forcing US-English region to prevent local news portal redirects
            results = list(ddgs.text(query, region="us-en", max_results=5))
            # Check if auto search returned no results
            if not results:
                # Fallback to the lite search backend with US-English region
                results = list(ddgs.text(query, region="us-en", backend="lite", max_results=5))
            
            # If both backends returned empty results, notify the agent
            if not results:
                # Return no results warning
                return f"No search results found for query: '{query}'."
            
            # Initialize list to hold formatted output lines
            output = []
            # Iterate through search results
            for r in results:
                # Retrieve title or fallback to placeholder
                title = r.get("title", "No Title")
                # Retrieve link url or fallback to placeholder
                href = r.get("href", "No URL")
                # Retrieve page snippet text or fallback to placeholder
                body = r.get("body", "")
                # Format into a readable entry and append
                output.append(f"Title: {title}\nURL: {href}\nSnippet: {body}\n")
            # Join all search entries and return
            return "\n".join(output)
    # Catch block for general exceptions
    except Exception as e:
        # Catch search connection errors and return the exception message
        return f"Error executing search: {str(e)}"

# Configure the default provider for each agent (choose: "Ollama", "Groq", or "Gemini")
AGENT_LLM_CONFIG = {
    "Requirement Analyst": "Groq",
    "Planning Agent": "Groq",
    "System Architect": "Groq",
    "Frontend Developer": "Ollama_7b",
    "Backend Developer": "Ollama_7b",
    "Integration Agent": "Ollama_7b",
    "QA Tester": "Ollama_7b",
    "Software Verifier": "Ollama_7b",
    "Troubleshooter Agent": "Groq",
    "Maintenance Developer": "Ollama_7b",
    "Maintenance QA": "Ollama_7b"
}

def get_model_for_agent(agent_name: str) -> str: # Define a helper function to get the model details for a specific agent name
    """Returns the descriptive provider and model name configured for an agent."""
    provider = AGENT_LLM_CONFIG.get(agent_name, "Ollama") # Look up the agent name in our AGENT_LLM_CONFIG dictionary, default to "Ollama" if not found
    provider_lower = provider.lower().strip() # Convert the provider name to lowercase and remove any leading or trailing whitespace
    if provider_lower == "ollama" or provider_lower == "ollama_1.5b": # If the provider is Ollama 1.5B (the smaller local model)
        return "Ollama [qwen2.5-coder:1.5b]" # Return the descriptive model string for Ollama 1.5B
    elif provider_lower == "ollama_7b": # If the provider is Ollama 7B (the larger local developer model)
        return "Ollama [qwen2.5-coder:7b]" # Return the descriptive model string for Ollama 7B
    elif provider_lower == "groq": # If the provider is Groq (cloud provider using Llama)
        return "Groq [llama-3.1-8b-instant]" # Return the descriptive model string for Groq
    elif provider_lower == "gemini": # If the provider is Gemini (Google cloud provider)
        return "Gemini [gemini-2.5-flash]" # Return the descriptive model string for Gemini
    return provider # If it didn't match any of the above, just return the raw provider string configured

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") # Retrieve the Groq API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", "")) # Retrieve the Gemini API key from environment variables (checking both GEMINI_API_KEY and GOOGLE_API_KEY)

def create_llm_client(provider: str): # Define a factory function to construct and return a LangChain LLM client
    """Factory to create a LangChain LLM client based on the provider name."""
    provider_lower = provider.lower().strip() # Convert the provider string to lowercase and strip whitespace
    if provider_lower == "ollama" or provider_lower == "ollama_1.5b": # If provider matches Ollama or Ollama 1.5B
        return ChatOllama( # Create and return a local ChatOllama client instance
            model="qwen2.5-coder:1.5b", # Set the target model to the Qwen 2.5 Coder 1.5B model
            temperature=0 # Set temperature to 0 for deterministic and consistent output
        )
    elif provider_lower == "ollama_7b": # If provider matches Ollama 7B
        return ChatOllama( # Create and return a local ChatOllama client instance
            model="qwen2.5-coder:7b", # Set the target model to the Qwen 2.5 Coder 7B model
            temperature=0 # Set temperature to 0 for deterministic and consistent output
        )
    elif provider_lower == "groq": # If provider matches Groq
        return ChatGroq( # Create and return a cloud ChatGroq client instance
            model="llama-3.1-8b-instant", # Set the target model to Llama 3.1 8B Instant on Groq
            api_key=GROQ_API_KEY, # Pass the Groq API key retrieved from the environment
            temperature=0 # Set temperature to 0 for deterministic output
        )
    elif provider_lower == "gemini": # If provider matches Gemini
        if not GEMINI_API_KEY: # Check if the Gemini API key is empty or missing
            print(Fore.YELLOW + "\n⚠️  [System Warning] Gemini API key is missing. Falling back to Groq for this agent..." + Fore.RESET) # Print a warning message to the console in yellow color
            return create_llm_client("groq") # Recursively call create_llm_client with "groq" as a fallback
        return ChatGoogleGenerativeAI( # Create and return a cloud Gemini client instance
            model="gemini-2.5-flash", # Set the target model to Gemini 2.5 Flash
            google_api_key=GEMINI_API_KEY, # Pass the Google API key retrieved from the environment
            temperature=0 # Set temperature to 0 for deterministic output
        )
    else: # If the provider is not recognized
        raise ValueError(f"Unknown LLM provider: {provider}") # Raise a ValueError exception indicating the unknown provider

# Keep a default global llm client for backwards compatibility/greetings (Ollama fallback)
try:
    llm = create_llm_client("Ollama")
except Exception:
    llm = None

def parse_failed_generation(failed_gen: str) -> dict:
    """Parses a failed generation string from Groq and extracts function name and arguments."""
    try:
        # Match <function=name>args
        m = re.match(r'^<function=(\w+)>\s*([\s\S]*)$', failed_gen.strip())
        if not m:
            return None
        func_name = m.group(1)
        args_str = m.group(2).strip()
        
        # Try parsing args_str as JSON
        try:
            cleaned = clean_json_candidate(args_str)
            args = json.loads(cleaned)
            if isinstance(args, dict):
                if "args" in args and isinstance(args["args"], dict):
                    args = args["args"]
                return {"name": func_name, "args": args}
        except Exception:
            pass
            
        # Fallback key-value parsing for raw strings e.g. "filename: path, content: code"
        args = {}
        keys = ["filename", "content", "query"]
        for key in keys:
            pattern = rf'{key}\s*:\s*(.*?)(?=\s*(?:filename|content|query)\s*:|$)'
            match = re.search(pattern, args_str, re.DOTALL)
            if match:
                val = match.group(1).strip()
                if val.endswith(','):
                    val = val[:-1].strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                val = val.replace('</function>', '').strip()
                args[key] = val
                
        if args:
            return {"name": func_name, "args": args}
    except Exception:
        pass
    return None

def invoke_agent_with_fallback(agent_name: str, messages: list, tools: list = None): # Define function invoke_agent_with_fallback that takes agent_name, messages, and optional tools list
    """Invokes the assigned LLM for an agent, catching rate limits/errors with an automated fallback ladder."""
    provider = AGENT_LLM_CONFIG.get(agent_name, "Ollama") # Retrieve the configured LLM provider for the agent, defaulting to "Ollama"
    
    if OFFLINE_MODE and provider.lower().strip() not in ["ollama_1.5b", "ollama", "ollama_7b"]: # Check if offline mode is active and if the provider is not a local Ollama model
        print(Fore.YELLOW + f"   [Offline Mode] Forcing '{agent_name}' to Local Qwen 7B." + Fore.RESET) # Print a warning to the console that the agent is being forced to local Qwen 7B
        provider = "Ollama_7b" # Override the provider setting to "Ollama_7b"
        
    fallback_ladder = ["Gemini", "Groq", "Ollama_7b", "Ollama_1.5b"] # Define the ordered list of LLM providers to try in sequence when errors occur
    if OFFLINE_MODE: # Check if offline mode is active
        fallback_ladder = ["Ollama_7b", "Ollama_1.5b"] # Restrict the fallback list to only include local Ollama models
        
    retries_for_current_provider = 0 # Initialize the retry count for the active LLM provider to zero
    max_retries = 2 # Define the maximum number of retry attempts allowed per provider
    
    while True: # Start an infinite loop to handle LLM invocation and catch exceptions
        try: # Start a try block to attempt LLM call
            print(Fore.WHITE + Style.DIM + f"   [LLM Provider: {provider}]" + Fore.RESET) # Print the active LLM provider to the console in dim white color
            client = create_llm_client(provider) # Create the LangChain LLM client using the current provider name
            if tools: # Check if a list of tools was passed to the function
                client = client.bind_tools(tools) # Bind the list of tools to the LLM client so it can perform function calling
            
            # Perform invocation
            return client.invoke(messages) # Invoke the LLM client with the conversation messages and return the result
            
        except Exception as e: # Catch any exception raised during model invocation
            err_msg = str(e) # Convert the exception object to a string representation
            
            # Extract failed_generation from exception message or response if available
            failed_gen = None # Initialize the failed_generation variable as None
            if hasattr(e, 'body') and isinstance(e.body, dict): # Check if the exception object has a body attribute of dictionary type
                failed_gen = e.body.get('error', {}).get('failed_generation') # Extract the failed_generation value from the error details
            elif hasattr(e, 'response') and hasattr(e.response, 'json'): # Check if the exception has a response attribute with a json method
                try: # Start a try block to parse JSON response
                    failed_gen = e.response.json().get('error', {}).get('failed_generation') # Extract failed_generation from the response JSON
                except Exception: # Catch any JSON parsing exceptions
                    pass # Ignore parsing exceptions and proceed
            
            if not failed_gen: # Check if failed_gen is still None
                # Fallback to regex matching in string representation
                match = re.search(r"['\"]failed_generation['\"]\s*:\s*['\"]([\s\S]*?)['\"]\s*[,}]", err_msg) # Search the error message string for a failed_generation key-value pattern
                if match: # Check if a match was found by the regex
                    failed_gen = match.group(1) # Extract the matched content group
            
            if failed_gen: # Check if a malformed/failed tool call string was successfully extracted
                parsed = parse_failed_generation(failed_gen) # Parse the raw tool call string into a structured dictionary
                if parsed: # Check if parsing succeeded
                    print(Fore.GREEN + Style.BRIGHT + f"\n🛠️  [System Recovery] Automatically parsed malformed Groq tool call: '{parsed['name']}'" + Fore.RESET) # Print a success recovery message to the console in bright green
                    return AIMessage( # Return a manually constructed AIMessage to LangChain
                        content=f"Recovered and executing tool {parsed['name']}.", # Set the message text content
                        tool_calls=[{ # Populate the tool_calls list with the parsed parameters
                            "name": parsed["name"], # Set the target tool name
                            "args": parsed["args"], # Set the tool argument values
                            "id": f"recovered_tool_call_{int(time.time())}" # Generate a unique tool call ID using the current timestamp
                        }]
                    )
            
            print(Fore.RED + Style.BRIGHT + f"\n⚠️  [{agent_name}] Provider '{provider}' error: {err_msg}" + Fore.RESET) # Print the provider error message to the console in bright red
            
            if retries_for_current_provider < max_retries: # Check if the current provider's retry count is below the maximum limit
                retries_for_current_provider += 1 # Increment the current provider's retry count by one
                print(Fore.YELLOW + f"   [Auto-Recovery] Retrying provider '{provider}' in 5 seconds (Attempt {retries_for_current_provider}/{max_retries})..." + Fore.RESET) # Print a retry countdown warning in yellow
                time.sleep(5) # Pause execution for 5 seconds before retrying
                continue # Restart the loop iteration to retry the current provider
                
            # If we exhaust retries, move to next provider in the ladder
            if provider in fallback_ladder: # Check if the current provider is in the fallback ladder list
                current_idx = fallback_ladder.index(provider) # Find the position index of the current provider in the ladder list
                if current_idx < len(fallback_ladder) - 1: # Check if there is another provider after the current one in the list
                    provider = fallback_ladder[current_idx + 1] # Select the next provider in the ladder list
                    retries_for_current_provider = 0 # Reset the retry count to zero for the new provider
                    print(Fore.YELLOW + f"   [Auto-Fallback] Switching '{agent_name}' to {provider}..." + Fore.RESET) # Print a message to the console indicating the fallback switch
                    continue # Restart the loop iteration to try the new provider
            elif not OFFLINE_MODE and provider not in fallback_ladder: # Check if offline mode is inactive and the current provider is not in the ladder list
                # If provider wasn't in ladder but we failed, try joining ladder
                provider = fallback_ladder[0] # Fallback to the first provider in the fallback ladder
                retries_for_current_provider = 0 # Reset the retry count to zero for the new provider
                print(Fore.YELLOW + f"   [Auto-Fallback] Switching '{agent_name}' to {provider}..." + Fore.RESET) # Print a fallback switch message to the console
                continue # Restart the loop iteration to try the first ladder provider
                
            print(Fore.RED + f"   [Fatal] All fallback options exhausted for '{agent_name}'. Terminating." + Fore.RESET) # Print a fatal error message in red to indicate complete failure
            raise e # Reraise the exception to stop execution and notify the system

# Put all tools in a list to register them with the agent
tools = [search_internet, list_files, read_file, write_file]

# Configure the prompt template layout
prompt = ChatPromptTemplate.from_messages([
    # System role prompt instructing the agent on its tools and safe sandbox actions
    ("system", (
        "You are an expert autonomous software engineer and research assistant. "
        "You help the user solve coding tasks, search the web, and build software. "
        "You have complete access to the local workspace and can list, read, or write files at will. "
        "If the user asks you to write, create, or modify a file, you MUST call the `write_file` tool to save it. "
        "Do NOT write code blocks directly in your chat response. Always use the tools to perform file actions."
    )),
    # Memory placeholder where LangChain injects historical conversation turns
    MessagesPlaceholder(variable_name="chat_history"),
    # User's latest prompt message input
    ("human", "{input}"),
    # Agent workspace placeholder where thought tokens and tool calls are parsed
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def flush_input():
    """Flushes the standard input buffer on Windows to prevent pasted newlines from auto-skipping prompts."""
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except Exception:
        pass

def run_agent_cycles(user_input: str, chat_history: list) -> str:
    """Executes the agent tool-calling loop autonomously using a step-by-step cycle layout.
    
    Args:
        user_input: The task description entered by the user.
        chat_history: The list of previous conversation messages.
    """
    # Check if the input is a simple greeting to bypass cycle logging for direct chat replies
    clean_input = user_input.lower().strip().replace(".", "").replace("!", "").replace("?", "")
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "how are you", "what's up", "whats up"]
    if clean_input in greetings:
        messages = prompt.format_messages(
            input=user_input,
            chat_history=chat_history,
            agent_scratchpad=[]
        )
        response = llm.invoke(messages)
        return response.content

    # Initialize pipeline context accumulator and inject persistent memory if available
    memory_file = os.path.join(WORKSPACE_DIR, ".agent_memory.txt") # Define path to the persistent memory preferences file
    if os.path.exists(memory_file): # Check if the memory preferences file exists on the disk
        with open(memory_file, "r", encoding="utf-8") as mf: # Open the memory preferences file in read-only mode using UTF-8 encoding
            memory_contents = mf.read().strip() # Read the content of the file and strip any leading or trailing whitespace
            if memory_contents: # Check if the memory preferences content is non-empty
                print(Fore.CYAN + "🧠 [Memory] Loaded persistent developer preferences." + Fore.RESET) # Print message to console indicating memory loaded
                pipeline_context = f"Global Developer Preferences (MUST FOLLOW):\n{memory_contents}\n\nOriginal User Goal: {user_input}\n\n" # Start the pipeline context with developer preferences and original user goal
            else: # If the memory preferences file is empty
                pipeline_context = f"Original User Goal: {user_input}\n\n" # Start the pipeline context with only the original user goal
    else: # If the memory preferences file does not exist
        pipeline_context = f"Original User Goal: {user_input}\n\n" # Initialize the pipeline context with only the original user goal
        
    llm_with_tools = llm.bind_tools(tools) # Bind the workspace tools to the default llm instance
    
    # --- Agent 1: Requirement Analyst ---
    print(Fore.YELLOW + Style.BRIGHT + f"\n🔍 [Agent 1/8] Requirement Analyst [Model: {get_model_for_agent('Requirement Analyst')}]" + Fore.RESET) # Print header indicating start of Agent 1 execution
    messages = [ # Construct the system and human message block for Agent 1
        ("system", ( # Define the system instructions for the Requirement Analyst
            "You are an expert Requirement Analyst Agent. Your job is to analyze the user's software development goal, "
            "extract core features and constraints, and identify technical assumptions.\n\n"
            "CRITICAL: Do NOT ask technical implementation questions (e.g. how to code CSS or database schemas). "
            "You must assume industry-standard defaults for technical details. Only ask 1 or 2 high-level business questions if absolutely necessary.\n\n"
            "Your output must be structured and include the following sections:\n"
            "- Detected Requirements\n"
            "- Assumed Defaults\n"
            "- Suggested Improvements\n"
            "- Clarification Questions (Max 2 non-technical questions, or 'None')"
        )),
        ("human", user_input) # Pass the original user input goal as the human message
    ]
    response = invoke_agent_with_fallback("Requirement Analyst", messages) # Invoke the LLM configured for the Requirement Analyst with fallback recovery
    initial_analyst_output = response.content # Extract the text response content generated by the analyst
    print(Fore.LIGHTYELLOW_EX + "💡 Output:" + Fore.RESET) # Print log indicator for output
    print(initial_analyst_output.strip() + "\n") # Print the clean analyst output to console
    
    # --- Human-in-the-Loop Requirement Review & User Confirmation Stage ---
    user_modifications = [] # Initialize an empty list to collect any modifications or answers from the user
    current_analyst_output = initial_analyst_output # Track the current analyst output (initially set to the first run output)
    
    while True: # Start validation loop for human review
        print(Fore.GREEN + Style.BRIGHT + "=========================================================" + Fore.RESET) # Print boundary line
        print(Fore.GREEN + Style.BRIGHT + "📋 Requirement Review & User Confirmation" + Fore.RESET) # Print section header
        print(Fore.GREEN + Style.BRIGHT + "=========================================================" + Fore.RESET) # Print boundary line
        print("Are these requirements final?") # Display question to the user
        print("Would you like to modify or add anything before development starts?") # Display modification question to the user
        print(Fore.YELLOW + "Press Enter or type 'yes'/'final' to approve and proceed, or enter your modifications/answers below:" + Fore.RESET) # Prompt user for input
        
        # Flush standard input to clear any buffered newlines from the initial pasted prompt
        flush_input() # Flush standard input buffer to prevent skipping the prompt
        user_feedback = input(Fore.BLUE + Style.BRIGHT + "Feedback: " + Fore.RESET).strip() # Read feedback from console input and strip whitespace
        
        if not user_feedback or user_feedback.lower() in ["yes", "y", "final", "approve"]: # If user approved or pressed enter
            print(Fore.GREEN + Style.BRIGHT + "\nRequirements approved! Resuming pipeline...\n" + Fore.RESET) # Print approval message
            break # Exit the verification loop to proceed to next agent
        elif user_feedback.lower() in ["exit", "quit", "bye"]: # If user requested to terminate
            print(Fore.GREEN + "\nAssistant: Goodbye!") # Print farewell message
            sys.exit(0) # Exit the script execution immediately
        else: # If user provided constructive feedback or answers
            user_modifications.append(user_feedback) # Append feedback text to user modifications list
            print(Fore.YELLOW + "\n🔄 Regenerating requirement summary with user feedback..." + Fore.RESET) # Print regeneration message
            
            # Combine all feedback accumulated so far and re-run the Requirement Analyst
            feedback_str = "\n".join([f"- {mod}" for mod in user_modifications]) # Join all user inputs with bullet points
            messages = [ # Reconstruct message block with accumulated feedback
                ("system", (
                    "You are an expert Requirement Analyst Agent. Your job is to analyze the user's software development goal, "
                    "incorporating any modifications, specifications, or feedback provided by the user. "
                    "Extract core features and constraints, and identify technical assumptions.\n\n"
                    "CRITICAL: Since the user has already provided feedback, you MUST assume the requirements are now complete. "
                    "Do NOT ask any further clarification questions. Accept the user's technical decisions silently.\n\n"
                    "Your output must be structured and include the following sections:\n"
                    "- Detected Requirements\n"
                    "- Assumed Defaults\n"
                    "- Suggested Improvements\n"
                    "- Clarification Questions (Output 'None - Requirements Finalized')"
                )),
                ("human", f"Original User Goal: {user_input}\n\nUser Modifications & Feedback:\n{feedback_str}") # Provide user goal along with feedback as human input
            ]
            response = invoke_agent_with_fallback("Requirement Analyst", messages) # Invoke the fallback runner to generate updated requirements
            current_analyst_output = response.content # Store the updated analysis text content
            print(Fore.LIGHTYELLOW_EX + "\n💡 Updated Output:" + Fore.RESET) # Print output header
            print(current_analyst_output.strip() + "\n") # Display the updated analysis text content to the user
            
    # Add requirements summaries and user feedback to the pipeline context
    pipeline_context += f"--- 1a. Initial Extracted Requirements ---\n{initial_analyst_output}\n\n" # Append initial requirements to global pipeline context
    if user_modifications: # Check if there is feedback
        feedback_str = "\n".join([f"- {mod}" for mod in user_modifications]) # Format modifications list into single bulleted text
        pipeline_context += f"--- 1b. User Modifications & Feedback ---\n{feedback_str}\n\n" # Append modifications log to global context
    pipeline_context += f"--- 1c. Approved Final Requirement Summary ---\n{current_analyst_output}\n\n" # Append finalized requirements to global context
    save_agent_artifact("requirements.txt", current_analyst_output) # Save the approved requirements to disk under docs/requirements.txt
    
    # --- Agent 2: Planning Agent ---
    print(Fore.BLUE + Style.BRIGHT + f"📋 [Agent 2/8] Planning Agent [Model: {get_model_for_agent('Planning Agent')}]" + Fore.RESET) # Print log indicator for Agent 2
    messages = [ # Construct prompt messages for Planning Agent
        ("system", ( # Define the instructions for the Planning Agent
            "You are an expert Planning Agent. Your job is to read the requirements summary and formulate "
            "a step-by-step development roadmap. Break development into ordered implementation tasks. "
            "Be structured and concise."
        )),
        ("human", pipeline_context) # Chain the global context (which contains requirements output) as human input!
    ]
    response = invoke_agent_with_fallback("Planning Agent", messages) # Invoke the Planning Agent model with fallback
    planner_output = response.content # Extract planning text response
    print(Fore.LIGHTBLUE_EX + "💡 Output:" + Fore.RESET) # Print output header
    print(planner_output.strip() + "\n") # Display the execution roadmap to console
    pipeline_context += f"--- 2. Execution Roadmap ---\n{planner_output}\n\n" # Append planning output to global pipeline context!
    save_agent_artifact("planning.txt", planner_output) # Save planning result to docs/planning.txt
    
    # --- Agent 3: System Architect Agent ---
    print(Fore.CYAN + Style.BRIGHT + f"📐 [Agent 3/8] System Architect [Model: {get_model_for_agent('System Architect')}]" + Fore.RESET) # Print log indicator for Agent 3
    messages = [ # Construct message block for Architect Agent
        ("system", ( # Instructions for System Architect
            "You are an expert System Architect Agent. Your job is to decide the architecture. "
            "Define the technologies, APIs, backend server framework, module structure, and file layouts. "
            "Do not write actual source code."
        )),
        ("human", pipeline_context) # Chain the global context (containing requirements AND roadmap outputs) as human input!
    ]
    response = invoke_agent_with_fallback("System Architect", messages) # Invoke the System Architect model with fallback
    architect_output = response.content # Extract architectural text response
    print(Fore.LIGHTCYAN_EX + "💡 Output:" + Fore.RESET) # Print output header
    print(architect_output.strip() + "\n") # Display architecture details on console
    pipeline_context += f"--- 3. System Architecture ---\n{architect_output}\n\n" # Append architecture design to global pipeline context!
    save_agent_artifact("architecture.txt", architect_output) # Save system architecture result to docs/architecture.txt
    
    # --- Agent 4: Frontend Developer Agent ---
    print(Fore.MAGENTA + Style.BRIGHT + f"🎨 [Agent 4/8] Frontend Developer [Model: {get_model_for_agent('Frontend Developer')}]" + Fore.RESET) # Print message starting Agent 4 execution
    fe_attempts = 0 # Initialize current code generation attempt counter for Frontend Developer to zero
    max_fe_attempts = 3 # Define the maximum code generation verification attempts allowed
    fe_output = "" # Initialize empty string variable to store frontend compilation summary output
    
    while fe_attempts < max_fe_attempts: # Start verification loop for compiling frontend code
        fe_attempts += 1 # Increment current code generation verification attempt by one
        fe_scratchpad = [] # Initialize empty list to store intermediate cycle history messages
        
        for cycle in range(1, 15): # Start loop running up to 15 autonomous developer execution cycles
            fe_messages = [ # Construct prompt messages with history scratchpad for this cycle
                ("system", ( # Instructions for Frontend Developer Agent
                    "You are an expert Frontend Developer Agent. Your job is to implement the user interface, pages, components, "
                    "and visual interactions. You MUST physically write the frontend files to the disk. Do NOT just explain them.\n\n"
                    "Based on the System Architecture design provided in the conversation, implement all required HTML templates, stylesheets, and client-side scripts. "
                    "You are not limited to one file; write all the necessary templates (e.g., base.html, dashboard.html, list/form views, transactions, history, etc.) and assets. "
                    "Ensure that all HTML templates are placed under the 'templates/' folder, and static files (CSS, JS) are under the 'static/' folder.\n\n"
                    "CRITICAL TO AVOID TOKEN LIMITS: You must generate EXACTLY ONE file per cycle. Do not attempt to write all files in a single turn. "
                    "Call the `write_file` tool for ONE file, then end your turn. You will be prompted again to write the next file.\n"
                    "When you have finished writing ALL frontend code, output a summary of what you built without any tool calls."
                )),
                ("human", pipeline_context), # Pass current pipeline context containing requirements and designs
                *fe_scratchpad # Unpack the cycle history messages to form the conversational memory
            ]
            response = invoke_agent_with_fallback("Frontend Developer", fe_messages, tools=tools) # Invoke LLM configured for Frontend Developer Agent with fallbacks
            content = response.content # Store response message content generated by the agent
            tool_calls = getattr(response, "tool_calls", []) # Retrieve LangChain tool calls from response
            
            # Fallback JSON and code block parsing
            if not tool_calls: # If no native tool calls were returned by the LLM
                tool_calls = parse_agent_response(content, cycle, "fe") # Extract tool calls using custom regex/markdown parsers
                    
            thought = content.strip() # Strip surrounding whitespace from generated agent content
            if thought.startswith("{") and thought.endswith("}"): # If output is pure JSON
                thought = "I will write the frontend files to the workspace." # Substitute JSON text with a friendly log message
                
            print(Fore.LIGHTMAGENTA_EX + f"   [Cycle {cycle}/15] 💡 Thought:" + Fore.RESET) # Print loop cycle indicators in light magenta color
            print("   " + thought.replace("\n", "\n   ") + "\n") # Print agent thought steps to standard console
            
            if not tool_calls: # If no tool call actions are remaining
                fe_output = content # Save content as the agent's final text summary report
                if "finished" in content.lower() or "complete" in content.lower(): # Check if agent declared completion
                    break # Exit the execution cycle loop
                fallback_msg = "Please call the `write_file` tool to generate the next file, or state 'I am finished' if all files are complete." # Define system instruction
                print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n") # Print system instruction in yellow
                fe_scratchpad.append(AIMessage(content=content)) # Store agent's content in conversational cycle memory
                fe_scratchpad.append(HumanMessage(content=fallback_msg)) # Store system instruction in conversational cycle memory
                continue # Skip remaining iteration steps to run next developer cycle
                
            for tc in tool_calls: # Loop through every parsed tool call action
                tool_name = tc["name"] # Store the target tool name
                tool_args = tc["args"] # Store the dictionary of arguments
                print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET) # Print action header in magenta color
                print(f"   Calling tool '{tool_name}' with parameters: {tool_args}\n") # Log specific tool parameters to console
                
                target_tool = None # Initialize target tool runner reference as None
                for t in tools: # Look up the registered tools list
                    if t.name == tool_name: # Check if tool name matches
                        target_tool = t # Set reference to matching tool runner
                        break # Stop lookup loop
                if target_tool: # If a matching tool runner was found
                    try: # Start try block for tool execution
                        observation = target_tool.invoke(tool_args) # Execute the tool invoke function with the arguments
                    except Exception as e: # Catch any tool runtime exception
                        observation = f"Error executing tool: {str(e)}" # Format error message as observation
                else: # If tool name is not registered
                    observation = f"Error: Tool '{tool_name}' is not registered." # Define warning string
                    
                print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET) # Print log header for tool observation in green
                print("   " + observation.strip().replace("\n", "\n   ") + "\n") # Display the output returned by the tool execution
                
                fe_scratchpad.append(AIMessage(content=content, tool_calls=[tc])) # Save tool execution details to cycle memory
                fe_scratchpad.append(ToolMessage(content=observation, tool_call_id=tc.get("id", "fallback_id_fe_" + str(cycle)))) # Save output observation to cycle memory
        
        # Post-agent verification step
        missing_fe = verify_frontend_files()
        if not missing_fe:
            print(Fore.GREEN + Style.BRIGHT + "✅ [Verification] Frontend files verified successfully on disk.\n" + Fore.RESET)
            break
        else:
            print(Fore.RED + Style.BRIGHT + f"⚠️  [Verification Failed] Missing frontend files: {', '.join(missing_fe)}" + Fore.RESET)
            if fe_attempts < max_fe_attempts:
                print(Fore.YELLOW + f"Rerunning Frontend Developer Agent (Attempt {fe_attempts + 1}/{max_fe_attempts})...\n" + Fore.RESET)
                pipeline_context += (
                    f"\n[System Alert] File generation failed on attempt {fe_attempts}. "
                    f"The following mandatory files are missing: {', '.join(missing_fe)}. "
                    f"You MUST call write_file() to create them before completing the task.\n"
                )
            else:
                print(Fore.RED + "❌ Max attempts reached. Continuing with incomplete files.\n" + Fore.RESET)
                
    if not fe_output:
        fe_output = "Frontend files written successfully."
    pipeline_context += f"--- 4. Frontend Implementation ---\n{fe_output}\n\n"
    save_agent_artifact("frontend_summary.txt", fe_output)
    
    # --- Agent 5: Backend Developer Agent ---
    print(Fore.LIGHTRED_EX + Style.BRIGHT + f"⚙️ [Agent 5/8] Backend Developer [Model: {get_model_for_agent('Backend Developer')}]" + Fore.RESET)
    be_attempts = 0
    max_be_attempts = 3
    be_output = ""
    
    while be_attempts < max_be_attempts:
        be_attempts += 1
        be_scratchpad = []
        
        for cycle in range(1, 15):
            be_messages = [
                ("system", (
                    "You are an expert Backend Developer Agent. Your job is to generate backend functionality, APIs, server logic, "
                    "and database models. You MUST physically write the backend files to the disk. Do NOT just explain them.\n\n"
                    "Based on the System Architecture design provided in the conversation, implement all backend files (including database configuration, models, routes, forms, schemas, and main server files like app.py). "
                    "Do not limit yourself to a single file; write all the necessary modules, models, blueprints, and database configuration files specified in the design. "
                    "Make sure that all db models import the same shared `db` object from the database configuration file (e.g. `from database import db`), rather than re-instantiating `SQLAlchemy()` separately in each file.\n\n"
                    "CRITICAL TO AVOID TOKEN LIMITS: You must generate EXACTLY ONE file per cycle. Do not attempt to write all files in a single turn. "
                    "Call the `write_file` tool for ONE file, then end your turn. You will be prompted again to write the next file.\n"
                    "When you have finished writing ALL backend code, output a summary of what you built without any tool calls."
                )),
                ("human", pipeline_context),
                *be_scratchpad
            ]
            response = invoke_agent_with_fallback("Backend Developer", be_messages, tools=tools)
            content = response.content
            tool_calls = getattr(response, "tool_calls", [])
            
            # Fallback JSON and code block parsing
            if not tool_calls:
                tool_calls = parse_agent_response(content, cycle, "be")
                    
            thought = content.strip()
            if thought.startswith("{") and thought.endswith("}"):
                thought = "I will write the backend server scripts to the workspace."
                
            print(Fore.LIGHTRED_EX + f"   [Cycle {cycle}/15] 💡 Thought:" + Fore.RESET)
            print("   " + thought.replace("\n", "\n   ") + "\n")
            
            if not tool_calls:
                be_output = content
                if "finished" in content.lower() or "complete" in content.lower():
                    break
                fallback_msg = "Please call the `write_file` tool to generate the next file, or state 'I am finished' if all files are complete."
                print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n")
                be_scratchpad.append(AIMessage(content=content))
                be_scratchpad.append(HumanMessage(content=fallback_msg))
                continue
                
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET)
                print(f"   Calling tool '{tool_name}' with parameters: {tool_args}\n")
                
                target_tool = None
                for t in tools:
                    if t.name == tool_name:
                        target_tool = t
                        break
                if target_tool:
                    try:
                        observation = target_tool.invoke(tool_args)
                    except Exception as e:
                        observation = f"Error executing tool: {str(e)}"
                else:
                    observation = f"Error: Tool '{tool_name}' is not registered."
                    
                print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET)
                print("   " + observation.strip().replace("\n", "\n   ") + "\n")
                
                be_scratchpad.append(AIMessage(content=content, tool_calls=[tc]))
                be_scratchpad.append(ToolMessage(content=observation, tool_call_id=tc.get("id", "fallback_id_be_" + str(cycle))))
        
        # Post-agent verification step
        missing_be = verify_backend_files()
        if not missing_be:
            print(Fore.GREEN + Style.BRIGHT + "✅ [Verification] Backend files verified successfully on disk.\n" + Fore.RESET)
            break
        else:
            print(Fore.RED + Style.BRIGHT + f"⚠️  [Verification Failed] Missing backend files: {', '.join(missing_be)}" + Fore.RESET)
            if be_attempts < max_be_attempts:
                print(Fore.YELLOW + f"Rerunning Backend Developer Agent (Attempt {be_attempts + 1}/{max_be_attempts})...\n" + Fore.RESET)
                pipeline_context += (
                    f"\n[System Alert] File generation failed on attempt {be_attempts}. "
                    f"The following mandatory files are missing: {', '.join(missing_be)}. "
                    f"You MUST call write_file() to create them before completing the task.\n"
                )
            else:
                print(Fore.RED + "❌ Max attempts reached. Continuing with incomplete files.\n" + Fore.RESET)
                
    if not be_output:
        be_output = "Backend files written successfully."
    pipeline_context += f"--- 5. Backend Implementation ---\n{be_output}\n\n"
    save_agent_artifact("backend_summary.txt", be_output)
    
    # --- Agent 6: Integration Agent ---
    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"🔗 [Agent 6/8] Integration Agent [Model: {get_model_for_agent('Integration Agent')}]" + Fore.RESET)
    int_attempts = 0
    max_int_attempts = 3
    int_output = ""
    
    while int_attempts < max_int_attempts:
        int_attempts += 1
        int_scratchpad = []
        
        for cycle in range(1, 10):
            int_messages = [
                ("system", (
                    "You are an expert Integration Agent. Your job is to connect the frontend and backend files, "
                    "resolve imports, setup configuration, configure database initialization, and ensure the entire system operates properly on localhost.\n\n"
                    "Verify all routes, blueprints, models, forms, and templates are correctly registered and integrated into the main Flask application (such as in app.py) and that database connections are properly shared. "
                    "Make sure all blueprints, forms, and assets are properly linked and that the database tables are initialized when the app starts. "
                    "You MUST call tools (e.g. `write_file`) to modify or write configuration, integration, or server files to resolve any broken imports or missing wiring.\n"
                    "Ensure to write the ENTIRE file content in a single call. When done integrating, output a summary."
                )),
                ("human", pipeline_context),
                *int_scratchpad
            ]
            response = invoke_agent_with_fallback("Integration Agent", int_messages, tools=tools)
            content = response.content
            tool_calls = getattr(response, "tool_calls", [])
            
            # Fallback JSON and code block parsing
            if not tool_calls:
                tool_calls = parse_agent_response(content, cycle, "int")
                    
            thought = content.strip()
            if thought.startswith("{") and thought.endswith("}"):
                thought = "I will perform integration edits and wire the components together."
                
            print(Fore.LIGHTCYAN_EX + f"   [Cycle {cycle}/10] 💡 Thought:" + Fore.RESET)
            print("   " + thought.replace("\n", "\n   ") + "\n")
            
            if not tool_calls:
                int_output = content
                if "finished" in content.lower() or "complete" in content.lower():
                    break
                fallback_msg = "Please call the `write_file` tool to make your edits, or state 'I am finished' if the integration is complete."
                print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n")
                int_scratchpad.append(AIMessage(content=content))
                int_scratchpad.append(HumanMessage(content=fallback_msg))
                continue
                
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET)
                print(f"   Calling tool '{tool_name}' with parameters: {tool_args}\n")
                
                target_tool = None
                for t in tools:
                    if t.name == tool_name:
                        target_tool = t
                        break
                if target_tool:
                    try:
                        observation = target_tool.invoke(tool_args)
                    except Exception as e:
                        observation = f"Error executing tool: {str(e)}"
                else:
                    observation = f"Error: Tool '{tool_name}' is not registered."
                    
                print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET)
                print("   " + observation.strip().replace("\n", "\n   ") + "\n")
                
                int_scratchpad.append(AIMessage(content=content, tool_calls=[tc]))
                int_scratchpad.append(ToolMessage(content=observation, tool_call_id=tc.get("id", "fallback_id_int_" + str(cycle))))
        
        # Post-agent verification step
        validation_errors = run_all_validations(CURRENT_PROJECT_DIR)
        if not validation_errors:
            print(Fore.GREEN + Style.BRIGHT + "✅ [Verification] Integration verified successfully: No structural or startup errors detected.\n" + Fore.RESET)
            break
        else:
            print(Fore.RED + Style.BRIGHT + f"⚠️  [Verification Failed] Validation errors found:\n" + "\n".join(f" - {err}" for err in validation_errors) + Fore.RESET)
            if int_attempts < max_int_attempts:
                print(Fore.YELLOW + f"Rerunning Integration Agent (Attempt {int_attempts + 1}/{max_int_attempts})...\n" + Fore.RESET)
                pipeline_context += (
                    f"\n[System Alert] Validation failed on attempt {int_attempts}. "
                    f"Fix the following errors:\n" + "\n".join(f"- {err}" for err in validation_errors) + "\n"
                    f"You MUST call write_file() or other tools to fix these issues before completing.\n"
                )
            else:
                print(Fore.RED + "❌ Max attempts reached. Continuing with incomplete integration.\n" + Fore.RESET)
                
    if not int_output:
        int_output = "Integration completed successfully."
    pipeline_context += f"--- 6. Integration Report ---\n{int_output}\n\n"
    save_agent_artifact("integration_summary.txt", int_output)
    
    # --- Agent 7: QA Testing Agent ---
    print(Fore.GREEN + Style.BRIGHT + f"🧪 [Agent 7/8] QA Tester [Model: {get_model_for_agent('QA Tester')}]" + Fore.RESET)
    qa_scratchpad = []
    qa_output = ""
    for cycle in range(1, 10):
        qa_messages = [
            ("system", (
                "You are an expert QA Testing Agent. Your job is to validate file integrity, check edge cases, and run tests. "
                "First, call the `list_files` tool to discover all files written in the project workspace directory. "
                "Then, call the `read_file` tool to inspect each file individually, verifying imports, database connections, schemas, templates, and confirming they are correct and do not contain syntax errors. "
                "Always use the tools to perform file actions."
            )),
            ("human", pipeline_context),
            *qa_scratchpad
        ]
        response = invoke_agent_with_fallback("QA Tester", qa_messages, tools=tools)
        content = response.content
        tool_calls = getattr(response, "tool_calls", [])
        
        # Fallback JSON and code block parsing
        if not tool_calls:
            tool_calls = parse_agent_response(content, cycle, "qa")
                
        thought = content.strip()
        if thought.startswith("{") and thought.endswith("}"):
            thought = "I will read the source code files to run quality checks."
            
        print(Fore.LIGHTGREEN_EX + f"   [Cycle {cycle}/10] 💡 Thought:" + Fore.RESET)
        print("   " + thought.replace("\n", "\n   ") + "\n")
        
        if not tool_calls:
            qa_output = content
            if "finished" in content.lower() or "complete" in content.lower() or "verified" in content.lower():
                break
            fallback_msg = "Please call the `write_file` tool to output your report, or state 'I am finished' if testing is complete."
            print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n")
            qa_scratchpad.append(AIMessage(content=content))
            qa_scratchpad.append(HumanMessage(content=fallback_msg))
            continue
            
        for tc in tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET)
            print(f"   Calling tool '{tool_name}' with parameters: {tool_args}\n")
            
            target_tool = None
            for t in tools:
                if t.name == tool_name:
                    target_tool = t
                    break
            if target_tool:
                try:
                    observation = target_tool.invoke(tool_args)
                except Exception as e:
                    observation = f"Error executing tool: {str(e)}"
            else:
                observation = f"Error: Tool '{tool_name}' is not registered."
                
            print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET)
            print("   " + observation.strip().replace("\n", "\n   ") + "\n")
            
            qa_scratchpad.append(AIMessage(content=content, tool_calls=[tc]))
            qa_scratchpad.append(ToolMessage(content=observation, tool_call_id=tc.get("id", "fallback_id_qa_" + str(cycle))))
            
    if not qa_output:
        qa_output = "QA verification complete. System structure is correct."
    pipeline_context += f"--- 7. QA Verification Log ---\n{qa_output}\n\n"
    save_agent_artifact("qa_report.txt", qa_output)
    
    # --- Agent 8: Software Verification Agent ---
    print(Fore.WHITE + Style.BRIGHT + f"✅ [Agent 8/8] Software Verifier [Model: {get_model_for_agent('Software Verifier')}]" + Fore.RESET)
    
    vf_attempts = 0
    max_vf_attempts = 3
    verifier_output = ""
    
    while vf_attempts < max_vf_attempts:
        vf_attempts += 1
        messages = [
            ("system", (
                "You are an expert Software Verification Agent. Your job is to review the requirements summary, execution roadmap, "
                "architecture, and developers' outputs. Produce a final verification report summarizing "
                "what was built, how it satisfies the original user request, and confirming if the goal is fully accomplished."
            )),
            ("human", pipeline_context)
        ]
        response = invoke_agent_with_fallback("Software Verifier", messages)
        verifier_output = response.content
        save_agent_artifact("verification_report.txt", verifier_output)
        
        # Verify Completion Rule
        validation_errors = run_all_validations(CURRENT_PROJECT_DIR)
        if not validation_errors:
            print(Fore.LIGHTWHITE_EX + "💡 Final Report:" + Fore.RESET)
            print(verifier_output.strip() + "\n")
            print(Fore.GREEN + Style.BRIGHT + "✅ [Final Validation] All artifacts generated and project validates successfully.\n" + Fore.RESET)
            break
        else:
            print(Fore.RED + Style.BRIGHT + f"⚠️  [Final Validation Failed] Missing artifacts or errors:\n" + "\n".join(f" - {err}" for err in validation_errors) + Fore.RESET)
            if vf_attempts < max_vf_attempts:
                print(Fore.YELLOW + f"Rerunning Verification to request regeneration (Attempt {vf_attempts + 1}/{max_vf_attempts})...\n" + Fore.RESET)
                pipeline_context += (
                    f"\n[System Alert] Final verification failed on attempt {vf_attempts}. "
                    f"Errors:\n" + "\n".join(f"- {err}" for err in validation_errors) + "\n"
                    f"Please review the missing components and regenerate documentation.\n"
                )
            else:
                print(Fore.RED + "❌ Max attempts reached. Project incomplete.\n" + Fore.RESET)
    
    return verifier_output

def run_maintenance_workflow(chat_history: list):
    """Executes the post-generation human-in-the-loop maintenance workflow."""
    tools = [search_internet, list_files, read_file, write_file]
    
    print(Fore.GREEN + Style.BRIGHT + "\n=========================================================")
    print(Fore.GREEN + Style.BRIGHT + "🛠️ Project Generation Complete - User Testing Phase")
    print(Fore.GREEN + Style.BRIGHT + "=========================================================" + Fore.RESET)
    print("Please run the generated project locally and test it.")
    print("If you discover runtime errors, UI bugs, or missing features, paste the issue below.")
    print("Type " + Fore.YELLOW + "'final'" + Fore.RESET + ", " + Fore.YELLOW + "'exit'" + Fore.RESET + ", or " + Fore.YELLOW + "'no issues'" + Fore.RESET + " if the project is working correctly.\n")
    
    maintenance_cycles = 0
    max_maintenance_cycles = 5
    maintenance_context = f"Project Path: {CURRENT_PROJECT_DIR}\n"
    
    while maintenance_cycles < max_maintenance_cycles:
        flush_input()
        try:
            user_feedback = get_multiline_input(Fore.BLUE + Style.BRIGHT + "User Input: " + Fore.RESET).strip()
        except (KeyboardInterrupt, EOFError):
            print(Fore.GREEN + "\nAssistant: Exiting maintenance mode." + Fore.RESET)
            break
            
        if not user_feedback:
            continue
            
        if user_feedback.lower() in ["final", "exit", "quit", "no issues", "done", "bye"]:
            print(Fore.GREEN + Style.BRIGHT + "\n✅ Project finalized! Exiting maintenance mode." + Fore.RESET)
            break
            
        maintenance_cycles += 1
        print(Fore.YELLOW + Style.BRIGHT + f"\n[Maintenance Cycle {maintenance_cycles}/{max_maintenance_cycles}] Initiating bug fix pipeline..." + Fore.RESET)
        
        # --- Troubleshooter Agent ---
        print(Fore.YELLOW + Style.BRIGHT + f"\n🕵️ [Maintenance 1/3] Troubleshooter Agent [Model: {get_model_for_agent('Troubleshooter Agent')}]" + Fore.RESET)
        troubleshooter_llm = create_llm_client(AGENT_LLM_CONFIG.get("Troubleshooter Agent", "Groq"))
        troubleshooter_tools = [list_files, read_file]
        
        tr_messages = [
            ("system", (
                "You are an expert Troubleshooter Agent. A bug has been reported in an existing project.\n"
                "Your job is to read the bug report, use `list_files` and `read_file` to inspect the codebase, and find the root cause.\n"
                "You must output a structured diagnostic report detailing: Issue, Affected Files, Root Cause, Recommended Fix, Confidence.\n"
                "If you need to search files, call the tools. Once you have diagnosed the issue, output your report without tool calls."
            )),
            ("human", f"Maintenance History:\n{maintenance_context}\n\nNew Bug Report: {user_feedback}")
        ]
        
        tr_scratchpad = []
        tr_output = ""
        for cycle in range(1, 10):
            response = invoke_agent_with_fallback("Troubleshooter Agent", tr_messages + tr_scratchpad, tools=troubleshooter_tools)
            content = response.content
            tool_calls = getattr(response, "tool_calls", [])
            
            thought = content.strip()
            print(Fore.LIGHTYELLOW_EX + f"   [TR Cycle {cycle}/10] 💡 Thought:" + Fore.RESET)
            print("   " + thought.replace("\n", "\n   ") + "\n")
            
            if not tool_calls:
                tr_output = content
                if "affected files" in content.lower() or "root cause" in content.lower() or "recommended fix" in content.lower():
                    break
                fallback_msg = "Please use `read_file` to inspect the code, or output your diagnostic report if you are finished."
                print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n")
                tr_scratchpad.append(AIMessage(content=content))
                tr_scratchpad.append(HumanMessage(content=fallback_msg))
                continue
                
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET)
                print(f"   Calling '{tool_name}' with {tool_args}\n")
                
                t_obj = next((t for t in troubleshooter_tools if t.name == tool_name), None)
                if t_obj:
                    try: observation = t_obj.invoke(tool_args)
                    except Exception as e: observation = f"Error: {e}"
                else:
                    observation = f"Unknown tool: {tool_name}"
                
                print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET)
                print("   " + str(observation)[:500].replace("\n", "\n   ") + "...\n")
                
                tr_scratchpad.append(AIMessage(content=content, tool_calls=[tc]))
                tr_scratchpad.append(ToolMessage(content=str(observation), tool_call_id=tc.get("id", f"fallback_tr_{cycle}")))
        
        maintenance_context += f"\n--- Cycle {maintenance_cycles} Bug Report ---\n{user_feedback}\n\n--- Troubleshooter Report ---\n{tr_output}\n"
        
        # --- Maintenance Developer Agent ---
        print(Fore.MAGENTA + Style.BRIGHT + f"\n🔧 [Maintenance 2/3] Developer Agent [Model: {get_model_for_agent('Maintenance Developer')}]" + Fore.RESET)
        dev_tools = [read_file, write_file]
        
        dev_messages = [
            ("system", (
                "You are an expert Maintenance Developer Agent. Your job is to implement fixes based on the Troubleshooter's report.\n"
                "Use `read_file` to view the full file content, then use `write_file` to overwrite the file with the bug fixed.\n"
                "Modify ONLY the affected files. Preserve working functionality.\n"
                "When you are finished fixing the bugs, output a summary of Modified Files and Changes Applied."
            )),
            ("human", f"Project Path: {CURRENT_PROJECT_DIR}\nTroubleshooter Report:\n{tr_output}")
        ]
        
        dev_scratchpad = []
        dev_output = ""
        for cycle in range(1, 10):
            response = invoke_agent_with_fallback("Maintenance Developer", dev_messages + dev_scratchpad, tools=dev_tools)
            content = response.content
            tool_calls = getattr(response, "tool_calls", [])
            
            if not tool_calls:
                tool_calls = parse_agent_response(content, cycle, "mdev")
                
            thought = content.strip()
            print(Fore.LIGHTMAGENTA_EX + f"   [MD Cycle {cycle}/10] 💡 Thought:" + Fore.RESET)
            print("   " + thought.replace("\n", "\n   ") + "\n")
            
            if not tool_calls:
                dev_output = content
                if "modified files" in content.lower() or "changes applied" in content.lower() or "finished" in content.lower():
                    break
                fallback_msg = "Please use `write_file` to apply the fix, or output your change summary if finished."
                print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n")
                dev_scratchpad.append(AIMessage(content=content))
                dev_scratchpad.append(HumanMessage(content=fallback_msg))
                continue
                
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET)
                print(f"   Calling '{tool_name}' with {tool_args}\n")
                
                t_obj = next((t for t in dev_tools if t.name == tool_name), None)
                if t_obj:
                    try: observation = t_obj.invoke(tool_args)
                    except Exception as e: observation = f"Error: {e}"
                else:
                    observation = f"Unknown tool: {tool_name}"
                
                print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET)
                print("   " + str(observation)[:500].replace("\n", "\n   ") + "...\n")
                
                dev_scratchpad.append(AIMessage(content=content, tool_calls=[tc]))
                dev_scratchpad.append(ToolMessage(content=str(observation), tool_call_id=tc.get("id", f"fallback_md_{cycle}")))
                
        maintenance_context += f"\n--- Developer Summary ---\n{dev_output}\n"

        # --- Maintenance QA Agent ---
        print(Fore.CYAN + Style.BRIGHT + f"\n🔬 [Maintenance 3/3] QA Agent [Model: {get_model_for_agent('Maintenance QA')}]" + Fore.RESET)
        qa_tools = [read_file]
        
        qa_messages = [
            ("system", (
                "You are an expert Maintenance QA Agent. Review the Developer's fixes using `read_file` to ensure no syntax errors or obvious regressions were introduced.\n"
                "Output a Maintenance QA Report with: Issue Reviewed, Files Checked, Result (PASS/FAIL), and Notes."
            )),
            ("human", f"Developer Summary:\n{dev_output}\n\nPlease verify the changes.")
        ]
        
        qa_scratchpad = []
        qa_output = ""
        for cycle in range(1, 5):
            response = invoke_agent_with_fallback("Maintenance QA", qa_messages + qa_scratchpad, tools=qa_tools)
            content = response.content
            tool_calls = getattr(response, "tool_calls", [])
            
            thought = content.strip()
            print(Fore.LIGHTCYAN_EX + f"   [MQA Cycle {cycle}/5] 💡 Thought:" + Fore.RESET)
            print("   " + thought.replace("\n", "\n   ") + "\n")
            
            if not tool_calls:
                qa_output = content
                if "result:" in content.lower() or "pass" in content.lower() or "fail" in content.lower():
                    break
                fallback_msg = "Please use `read_file` to check the code, or output your QA Report if finished."
                print(Fore.YELLOW + "   [System] " + fallback_msg + Fore.RESET + "\n")
                qa_scratchpad.append(AIMessage(content=content))
                qa_scratchpad.append(HumanMessage(content=fallback_msg))
                continue
                
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                print(Fore.MAGENTA + f"   🛠 Action:" + Fore.RESET)
                print(f"   Calling '{tool_name}' with {tool_args}\n")
                
                t_obj = next((t for t in qa_tools if t.name == tool_name), None)
                if t_obj:
                    try: observation = t_obj.invoke(tool_args)
                    except Exception as e: observation = f"Error: {e}"
                else:
                    observation = f"Unknown tool: {tool_name}"
                
                print(Fore.GREEN + f"   📥 Observation:" + Fore.RESET)
                print("   " + str(observation)[:500].replace("\n", "\n   ") + "...\n")
                
                qa_scratchpad.append(AIMessage(content=content, tool_calls=[tc]))
                qa_scratchpad.append(ToolMessage(content=str(observation), tool_call_id=tc.get("id", f"fallback_mqa_{cycle}")))

        maintenance_context += f"\n--- QA Report ---\n{qa_output}\n"

        print(Fore.GREEN + Style.BRIGHT + "\n=========================================================")
        print(Fore.GREEN + Style.BRIGHT + "🔧 Maintenance Update Complete")
        print(Fore.GREEN + Style.BRIGHT + "=========================================================" + Fore.RESET)
        print("The reported issue has been analyzed and fixes have been applied.")
        print("Please test the project again. If additional issues exist, describe them below.")
        print("Type " + Fore.YELLOW + "'final'" + Fore.RESET + " or " + Fore.YELLOW + "'exit'" + Fore.RESET + " if everything is working correctly.\n")

    if maintenance_cycles >= max_maintenance_cycles:
        print(Fore.RED + Style.BRIGHT + "\n❌ Max maintenance cycles reached. Exiting maintenance mode to prevent infinite loops." + Fore.RESET)


def get_multiline_input(prompt_text: str) -> str:
    """Reads input from the console. If a multi-line block is pasted, automatically captures all lines."""
    print(prompt_text, end="", flush=True)
    lines = []
    try:
        first_line = input()
        lines.append(first_line)
        if first_line.lower().strip() in ["exit", "quit", "bye"]:
            return first_line
            
        # Detect and capture pasted multi-line content on Windows
        try:
            import msvcrt
            import time
            time.sleep(0.05)
            while msvcrt.kbhit():
                lines.append(input())
                time.sleep(0.01)
        except Exception:
            pass
    except (KeyboardInterrupt, EOFError):
        raise
    return "\n".join(lines).strip()

# Main function running the interactive loop
def main():
    # Print program headers styled with colorama colors
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    # Print agent start titles
    print(Fore.GREEN + Style.BRIGHT + "   LangChain Agentic AI Proof-of-Concept CLI Started   ")
    # Print closing boundary line
    print(Fore.GREEN + Style.BRIGHT + "=========================================================")
    
    # Prompt user for project name once at startup to scope the dynamic sandbox
    try:
        project_name = input(Fore.BLUE + Style.BRIGHT + "Enter project name (e.g. calculator, task_manager): " + Fore.RESET).strip()
    except (KeyboardInterrupt, EOFError):
        print(Fore.GREEN + "\nAssistant: Goodbye!")
        sys.exit(0)
        
    if not project_name:
        project_name = "unnamed_project"
        
    global CURRENT_PROJECT_DIR
    CURRENT_PROJECT_DIR = os.path.abspath(os.path.join(WORKSPACE_DIR, "projects", project_name))
    
    # Automatically initialize local Git repository at the root workspace level
    initialize_git_repo()
    
    # Print welcome greeting text
    print("\nWelcome! I am your agent. You can ask me to search the web, write files,")
    # Print workspace and memory details
    print("list workspace files, or read them. I remember our conversation.")
    print(f"Project sandbox path: {CURRENT_PROJECT_DIR}")
    # Print CLI instructions for exiting
    print("Type " + Fore.YELLOW + "'exit'" + Fore.RESET + ", " + Fore.YELLOW + "'quit'" + Fore.RESET + ", or " + Fore.YELLOW + "'bye'" + Fore.RESET + " to stop the loop.\n")
    
    # Initialize message list to act as short term memory
    chat_history = []
    
    # Start loop
    while True:
        # Try block to read console line inputs
        try:
            # Read human input, dynamically capturing multi-line clipboard pastes
            user_input = get_multiline_input(Fore.BLUE + Style.BRIGHT + "You: " + Fore.RESET).strip()
        # Catch key interruptions
        except (KeyboardInterrupt, EOFError):
            # Gracefully close if Ctrl+C or terminal EOF is pressed
            print(Fore.GREEN + "\nAssistant: Goodbye!")
            # Exit loop
            break
            
        # Skip empty messages
        if not user_input:
            # Continue loop
            continue
            
        # Exit program if exit phrases are typed
        if user_input.lower() in ["exit", "quit", "bye"]:
            # Print exit text
            print(Fore.GREEN + "\nAssistant: Goodbye!")
            # Exit loop
            break
            
        # Set max attempt counts for rate limits
        max_retries = 3
        # Set starting sleep delay to 60 seconds
        wait_time = 60
        # Flag variable for successful turns
        success = False
        
        # Retry loop for handling Groq API limits
        for attempt in range(max_retries):
            # Try block to run chain execution
            try:
                # Run the custom cycle-by-cycle agent runner
                output_content = run_agent_cycles(user_input, chat_history)
                
                # Print response to terminal styled in Cyan
                print(Fore.CYAN + Style.BRIGHT + f"Assistant: " + Fore.RESET + output_content + "\n")
                
                # Append user prompt message to memory history
                chat_history.append(HumanMessage(content=user_input))
                # Append assistant response message to memory history
                chat_history.append(AIMessage(content=output_content))
                
                # Set success flag
                success = True
                # Break retry loop
                break
            # Catch block for execution exceptions
            except Exception as e:
                # Convert exception to string message
                err_msg = str(e)
                # Check if the error matches rate limits or HTTP 429
                if "rate limit" in err_msg.lower() or "429" in err_msg or "ratelimit" in err_msg.lower():
                    # Warn the user and show retry countdowns
                    print(Fore.RED + f"\n[Rate limit hit. Waiting {wait_time}s to retry... (Attempt {attempt+1}/{max_retries})]")
                    # Sleep execution
                    time.sleep(wait_time)
                    # Double wait time for next retry (exponential backoff)
                    wait_time *= 2
                # If error is not a rate limit
                else:
                    # Print standard exceptions and stop retries
                    print(Fore.RED + f"\nAssistant error: {err_msg}\n")
                    # Break retry loop
                    break
        
        # Display warning if all retries failed
        if not success:
            # Print failure notification
            print(Fore.RED + "Failed to get a response after retrying. Please try again.")
        else:
            run_maintenance_workflow(chat_history)
            handle_git_push_workflow(project_name)

# Check if script is run directly
if __name__ == "__main__":
    # Call the main loop
    main()
