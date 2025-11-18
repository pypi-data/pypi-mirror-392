"""
AbuINSTALL - Package installer for AbuLang
Works like: from AbuINSTALL install module
Basically a friendly wrapper around pip
"""

import subprocess
import sys
import importlib

class AbuINSTALL:
    """Package installation utilities"""
    
    @staticmethod
    def install(package_name, upgrade=False):
        """
        Install a Python package using pip
        
        Args:
            package_name: Name of the package to install
            upgrade: Whether to upgrade if already installed
        
        Usage in AbuLang:
            from AbuINSTALL install requests
            from AbuINSTALL install numpy
        """
        try:
            print(f"[AbuINSTALL] Installing {package_name}...")
            
            cmd = [sys.executable, "-m", "pip", "install"]
            
            if upgrade:
                cmd.append("--upgrade")
            
            cmd.append(package_name)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[AbuINSTALL] ✓ Successfully installed {package_name}")
                
                # Try to import it to verify
                try:
                    importlib.import_module(package_name)
                    print(f"[AbuINSTALL] ✓ {package_name} is ready to use!")
                except:
                    print(f"[AbuINSTALL] Package installed but import name might be different")
                
                return True
            else:
                print(f"[AbuINSTALL] ✗ Failed to install {package_name}")
                print(f"[AbuINSTALL] Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[AbuINSTALL Error] {e}")
            return False
    
    @staticmethod
    def uninstall(package_name):
        """
        Uninstall a Python package
        
        Args:
            package_name: Name of the package to uninstall
        """
        try:
            print(f"[AbuINSTALL] Uninstalling {package_name}...")
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[AbuINSTALL] ✓ Successfully uninstalled {package_name}")
                return True
            else:
                print(f"[AbuINSTALL] ✗ Failed to uninstall {package_name}")
                print(f"[AbuINSTALL] Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[AbuINSTALL Error] {e}")
            return False
    
    @staticmethod
    def upgrade(package_name):
        """
        Upgrade a Python package to latest version
        
        Args:
            package_name: Name of the package to upgrade
        """
        return AbuINSTALL.install(package_name, upgrade=True)
    
    @staticmethod
    def list_installed():
        """List all installed packages"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("[AbuINSTALL] Installed packages:")
                print(result.stdout)
                return result.stdout
            else:
                print("[AbuINSTALL] Could not list packages")
                return None
                
        except Exception as e:
            print(f"[AbuINSTALL Error] {e}")
            return None
    
    @staticmethod
    def search(query):
        """
        Search for packages (note: pip search is currently disabled)
        
        Args:
            query: Search term
        """
        print(f"[AbuINSTALL] Searching for '{query}'...")
        print(f"[AbuINSTALL] Note: pip search is currently disabled by PyPI")
        print(f"[AbuINSTALL] Visit https://pypi.org/search/?q={query} to search")
        
        import webbrowser
        webbrowser.open(f"https://pypi.org/search/?q={query}")
    
    @staticmethod
    def show(package_name):
        """
        Show information about an installed package
        
        Args:
            package_name: Name of the package
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[AbuINSTALL] Package info for {package_name}:")
                print(result.stdout)
                return result.stdout
            else:
                print(f"[AbuINSTALL] Package {package_name} not found")
                return None
                
        except Exception as e:
            print(f"[AbuINSTALL Error] {e}")
            return None
    
    @staticmethod
    def check(package_name):
        """
        Check if a package is installed
        
        Args:
            package_name: Name of the package to check
        
        Returns:
            bool: True if installed, False otherwise
        """
        try:
            importlib.import_module(package_name)
            print(f"[AbuINSTALL] ✓ {package_name} is installed")
            return True
        except ImportError:
            print(f"[AbuINSTALL] ✗ {package_name} is not installed")
            return False
    
    @staticmethod
    def requirements(file_path="requirements.txt"):
        """
        Install packages from requirements file
        
        Args:
            file_path: Path to requirements.txt file
        """
        try:
            print(f"[AbuINSTALL] Installing from {file_path}...")
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[AbuINSTALL] ✓ Successfully installed all requirements")
                return True
            else:
                print(f"[AbuINSTALL] ✗ Failed to install requirements")
                print(f"[AbuINSTALL] Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[AbuINSTALL Error] {e}")
            return False
    
    @staticmethod
    def freeze(file_path="requirements.txt"):
        """
        Save currently installed packages to requirements file
        
        Args:
            file_path: Path to save requirements.txt
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                with open(file_path, 'w') as f:
                    f.write(result.stdout)
                print(f"[AbuINSTALL] ✓ Saved requirements to {file_path}")
                return True
            else:
                print(f"[AbuINSTALL] ✗ Failed to freeze requirements")
                return False
                
        except Exception as e:
            print(f"[AbuINSTALL Error] {e}")
            return False


# Create singleton instance
installer = AbuINSTALL()

# Convenience function for "from AbuINSTALL install package" syntax
def install(package_name):
    """Convenience function for installing packages"""
    return AbuINSTALL.install(package_name)
