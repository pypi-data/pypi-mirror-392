"""
AbuINSTALL - Package Manager
"""

import subprocess
import sys
import webbrowser

def install(package):
    """Install a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def uninstall(package):
    """Uninstall a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        print(f"✓ Uninstalled {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to uninstall {package}")
        return False

def upgrade(package):
    """Upgrade a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        print(f"✓ Upgraded {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to upgrade {package}")
        return False

def check(package):
    """Check if package is installed"""
    try:
        __import__(package)
        print(f"✓ {package} is installed")
        return True
    except ImportError:
        print(f"✗ {package} is not installed")
        return False

def show(package):
    """Show package information"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError:
        print(f"Package {package} not found")

def list_installed():
    """List all installed packages"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("Failed to list packages")

def requirements(filename):
    """Install from requirements file"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", filename])
        print(f"✓ Installed from {filename}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install from {filename}")
        return False

def freeze(filename):
    """Save current packages to requirements file"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True
        )
        with open(filename, 'w') as f:
            f.write(result.stdout)
        print(f"✓ Saved to {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to save: {e}")
        return False

def search(package):
    """Search for package (opens PyPI in browser)"""
    url = f"https://pypi.org/search/?q={package}"
    webbrowser.open(url)
    print(f"Opened PyPI search for: {package}")
