"""
AbuFILES - File Operations Package
"""

import os
import json
import pickle
from datetime import datetime

def create(filename, extension, content=""):
    """Create a file"""
    full_name = f"{filename}{extension}"
    with open(full_name, 'w') as f:
        f.write(content)
    return full_name

def read(filename):
    """Read file contents"""
    with open(filename, 'r') as f:
        return f.read()

def write(filename, content):
    """Write to file (overwrite)"""
    with open(filename, 'w') as f:
        f.write(content)

def append(filename, content):
    """Append to file"""
    with open(filename, 'a') as f:
        f.write(content)

def delete(filename):
    """Delete file"""
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False

def exists(filename):
    """Check if file exists"""
    return os.path.exists(filename)

def list_files(directory=".", extension=None):
    """List files in directory"""
    files = os.listdir(directory)
    if extension:
        files = [f for f in files if f.endswith(extension)]
    return files

def info(filename):
    """Get file information"""
    if os.path.exists(filename):
        stat = os.stat(filename)
        print(f"File: {filename}")
        print(f"Size: {stat.st_size} bytes")
        print(f"Modified: {datetime.fromtimestamp(stat.st_mtime)}")
        return stat
    return None

def save_data(filename, data):
    """Save data to .abudata file (JSON)"""
    full_name = f"{filename}.abudata"
    with open(full_name, 'w') as f:
        json.dump(data, f, indent=2)
    return full_name

def load_data(filename):
    """Load data from .abudata file"""
    full_name = f"{filename}.abudata"
    with open(full_name, 'r') as f:
        return json.load(f)

def save_config(filename, config):
    """Save config to .abuconfig file (JSON)"""
    full_name = f"{filename}.abuconfig"
    with open(full_name, 'w') as f:
        json.dump(config, f, indent=2)
    return full_name

def load_config(filename):
    """Load config from .abuconfig file"""
    full_name = f"{filename}.abuconfig"
    with open(full_name, 'r') as f:
        return json.load(f)

def log(filename, message):
    """Append to .abulog file with timestamp"""
    full_name = f"{filename}.abulog"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(full_name, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def read_log(filename):
    """Read .abulog file"""
    full_name = f"{filename}.abulog"
    if os.path.exists(full_name):
        with open(full_name, 'r') as f:
            return f.read()
    return ""

def save_game(filename, state):
    """Save game state to .abusave file (Pickle)"""
    full_name = f"{filename}.abusave"
    with open(full_name, 'wb') as f:
        pickle.dump(state, f)
    return full_name

def load_game(filename):
    """Load game state from .abusave file"""
    full_name = f"{filename}.abusave"
    with open(full_name, 'rb') as f:
        return pickle.load(f)

def list_types():
    """List all AbuLang file types"""
    types = {
        ".abu": "AbuLang Script",
        ".abudata": "Data File (JSON)",
        ".abuconfig": "Config File (JSON)",
        ".abulog": "Log File",
        ".abusave": "Save File (Pickle)",
        ".abudb": "Database File",
        ".abutest": "Test File"
    }
    print("=== AbuLang File Types ===")
    for ext, desc in types.items():
        print(f"{ext:15} - {desc}")
