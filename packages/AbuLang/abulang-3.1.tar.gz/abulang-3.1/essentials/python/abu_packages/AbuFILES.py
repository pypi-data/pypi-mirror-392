"""
AbuFILES - File type system for AbuLang
Create specialized .abu file types for different purposes
"""

import os
import json
import pickle

class AbuFILES:
    """File utilities and specialized file types"""
    
    # File type registry
    FILE_TYPES = {
        ".abu": "AbuLang Script",
        ".abudata": "AbuLang Data File (JSON)",
        ".abuconfig": "AbuLang Config File",
        ".abulog": "AbuLang Log File",
        ".abusave": "AbuLang Save File (Pickle)",
        ".abudb": "AbuLang Database File",
        ".abutest": "AbuLang Test File",
    }
    
    @staticmethod
    def create(filename, file_type=".abu", content=""):
        """
        Create a new Abu file
        
        Args:
            filename: Name of the file (without extension)
            file_type: Type of file to create
            content: Initial content
        """
        if not filename.endswith(file_type):
            filename = filename + file_type
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"[AbuFILES] ✓ Created {filename}")
            return filename
        except Exception as e:
            print(f"[AbuFILES Error] Could not create {filename}: {e}")
            return None
    
    @staticmethod
    def read(filename):
        """
        Read an Abu file
        
        Args:
            filename: Name of the file to read
        
        Returns:
            File content as string
        """
        try:
            with open(filename, 'r') as f:
                content = f.read()
            print(f"[AbuFILES] ✓ Read {filename} ({len(content)} chars)")
            return content
        except Exception as e:
            print(f"[AbuFILES Error] Could not read {filename}: {e}")
            return None
    
    @staticmethod
    def write(filename, content):
        """
        Write to an Abu file
        
        Args:
            filename: Name of the file
            content: Content to write
        """
        try:
            with open(filename, 'w') as f:
                f.write(str(content))
            print(f"[AbuFILES] ✓ Wrote to {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not write to {filename}: {e}")
            return False
    
    @staticmethod
    def append(filename, content):
        """
        Append to an Abu file
        
        Args:
            filename: Name of the file
            content: Content to append
        """
        try:
            with open(filename, 'a') as f:
                f.write(str(content))
            print(f"[AbuFILES] ✓ Appended to {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not append to {filename}: {e}")
            return False
    
    @staticmethod
    def delete(filename):
        """
        Delete an Abu file
        
        Args:
            filename: Name of the file to delete
        """
        try:
            os.remove(filename)
            print(f"[AbuFILES] ✓ Deleted {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not delete {filename}: {e}")
            return False
    
    @staticmethod
    def exists(filename):
        """
        Check if file exists
        
        Args:
            filename: Name of the file
        
        Returns:
            bool: True if exists
        """
        exists = os.path.exists(filename)
        if exists:
            print(f"[AbuFILES] ✓ {filename} exists")
        else:
            print(f"[AbuFILES] ✗ {filename} does not exist")
        return exists
    
    @staticmethod
    def list_files(directory=".", extension=".abu"):
        """
        List all Abu files in directory
        
        Args:
            directory: Directory to search
            extension: File extension to filter
        
        Returns:
            List of filenames
        """
        try:
            files = [f for f in os.listdir(directory) if f.endswith(extension)]
            print(f"[AbuFILES] Found {len(files)} {extension} files:")
            for f in files:
                print(f"  - {f}")
            return files
        except Exception as e:
            print(f"[AbuFILES Error] Could not list files: {e}")
            return []
    
    # ===== SPECIALIZED FILE TYPES =====
    
    @staticmethod
    def save_data(filename, data):
        """
        Save data to .abudata file (JSON format)
        
        Args:
            filename: Name of the file (auto-adds .abudata)
            data: Data to save (dict, list, etc.)
        """
        if not filename.endswith(".abudata"):
            filename = filename + ".abudata"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[AbuFILES] ✓ Saved data to {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not save data: {e}")
            return False
    
    @staticmethod
    def load_data(filename):
        """
        Load data from .abudata file (JSON format)
        
        Args:
            filename: Name of the file
        
        Returns:
            Loaded data
        """
        if not filename.endswith(".abudata"):
            filename = filename + ".abudata"
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"[AbuFILES] ✓ Loaded data from {filename}")
            return data
        except Exception as e:
            print(f"[AbuFILES Error] Could not load data: {e}")
            return None
    
    @staticmethod
    def save_config(filename, config):
        """
        Save config to .abuconfig file
        
        Args:
            filename: Name of the file (auto-adds .abuconfig)
            config: Config dict
        """
        if not filename.endswith(".abuconfig"):
            filename = filename + ".abuconfig"
        
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"[AbuFILES] ✓ Saved config to {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not save config: {e}")
            return False
    
    @staticmethod
    def load_config(filename):
        """
        Load config from .abuconfig file
        
        Args:
            filename: Name of the file
        
        Returns:
            Config dict
        """
        if not filename.endswith(".abuconfig"):
            filename = filename + ".abuconfig"
        
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            print(f"[AbuFILES] ✓ Loaded config from {filename}")
            return config
        except Exception as e:
            print(f"[AbuFILES Error] Could not load config: {e}")
            return {}
    
    @staticmethod
    def log(filename, message):
        """
        Append log message to .abulog file
        
        Args:
            filename: Name of the log file (auto-adds .abulog)
            message: Log message
        """
        if not filename.endswith(".abulog"):
            filename = filename + ".abulog"
        
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            with open(filename, 'a') as f:
                f.write(log_entry)
            print(f"[AbuFILES] ✓ Logged to {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not log: {e}")
            return False
    
    @staticmethod
    def read_log(filename):
        """
        Read log file
        
        Args:
            filename: Name of the log file
        
        Returns:
            Log content as string
        """
        if not filename.endswith(".abulog"):
            filename = filename + ".abulog"
        
        return AbuFILES.read(filename)
    
    @staticmethod
    def save_game(filename, game_state):
        """
        Save game state to .abusave file (Pickle format)
        
        Args:
            filename: Name of the save file (auto-adds .abusave)
            game_state: Game state object (any Python object)
        """
        if not filename.endswith(".abusave"):
            filename = filename + ".abusave"
        
        try:
            with open(filename, 'wb') as f:
                pickle.dump(game_state, f)
            print(f"[AbuFILES] ✓ Saved game to {filename}")
            return True
        except Exception as e:
            print(f"[AbuFILES Error] Could not save game: {e}")
            return False
    
    @staticmethod
    def load_game(filename):
        """
        Load game state from .abusave file
        
        Args:
            filename: Name of the save file
        
        Returns:
            Game state object
        """
        if not filename.endswith(".abusave"):
            filename = filename + ".abusave"
        
        try:
            with open(filename, 'rb') as f:
                game_state = pickle.load(f)
            print(f"[AbuFILES] ✓ Loaded game from {filename}")
            return game_state
        except Exception as e:
            print(f"[AbuFILES Error] Could not load game: {e}")
            return None
    
    @staticmethod
    def info(filename):
        """
        Get file information
        
        Args:
            filename: Name of the file
        
        Returns:
            Dict with file info
        """
        try:
            stat = os.stat(filename)
            info = {
                "name": filename,
                "size": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": os.path.splitext(filename)[1]
            }
            
            print(f"[AbuFILES] File info for {filename}:")
            print(f"  Size: {info['size_kb']} KB")
            print(f"  Extension: {info['extension']}")
            
            return info
        except Exception as e:
            print(f"[AbuFILES Error] Could not get file info: {e}")
            return None
    
    @staticmethod
    def list_types():
        """List all Abu file types"""
        print("[AbuFILES] Available file types:")
        for ext, desc in AbuFILES.FILE_TYPES.items():
            print(f"  {ext:15} - {desc}")
        return AbuFILES.FILE_TYPES


# Create singleton instance
files = AbuFILES()
