"""
File Operations Handler for AbuLang Multi-Format Block System

This module provides the FileOperations class that handles file save/load operations,
including save_as(), append_as(), and get_line() functions.
"""

import os


class FileOperations:
    """Handle file save/load operations with format detection and validation"""
    
    def __init__(self, context):
        """
        Initialize file operations handler
        
        Args:
            context: AbuRunner context dictionary for variable access
        """
        self.context = context
        self.saved_files = {}  # Track saved files with metadata
    
    def save_as(self, filename, content, format_type=None):
        """
        Save content to file
        
        Args:
            filename: Target filename with extension
            content: Content to save
            format_type: Optional format type for validation
        
        Returns:
            str: filename (for variable assignment) or None on error
        """
        try:
            # Validate content if format specified
            if format_type and format_type not in ['txt', 'pythonAL', 'python']:
                from essentials.python.format_context import FormatContext
                validator = FormatContext()
                validator.current_format = format_type
                validator.block_content = content.split('\n')
                valid, error = validator.validate_block()
                
                if not valid:
                    print(f"[AbuLang Error] {error}")
                    return None
            
            # Write file with UTF-8 encoding
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Track saved file with metadata
            self.saved_files[filename] = {
                'path': os.path.abspath(filename),
                'format': format_type or self._detect_format(filename),
                'size': len(content)
            }
            
            print(f"[AbuLang] ✓ Saved to {filename}")
            return filename
            
        except PermissionError:
            print(f"[AbuLang Error] Permission denied: Cannot write to {filename}")
            print(f"[AbuLang] Suggestion: Check file permissions or try saving to a different location")
            return None
        except OSError as e:
            if e.errno == 28:  # No space left on device
                print(f"[AbuLang Error] Disk space full: Cannot save {filename}")
                print(f"[AbuLang] Suggestion: Free up disk space or save to a different drive")
            elif e.errno == 22:  # Invalid argument (often bad filename)
                print(f"[AbuLang Error] Invalid filename: {filename}")
                print(f"[AbuLang] Suggestion: Avoid special characters like < > : \" / \\ | ? *")
            else:
                print(f"[AbuLang Error] Could not save {filename}: {e}")
                print(f"[AbuLang] Suggestion: Check that the directory exists and you have write permissions")
            return None
        except Exception as e:
            print(f"[AbuLang Error] Could not save {filename}: {e}")
            print(f"[AbuLang] Suggestion: Verify the filename is valid and the path is accessible")
            return None
    
    def append_as(self, filename, content):
        """
        Append content to file
        
        Args:
            filename: Target filename
            content: Content to append
        
        Returns:
            str: filename (for variable assignment) or None on error
        """
        try:
            # Check if file exists and if it ends with newline
            needs_newline = False
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    f.seek(0, 2)  # Seek to end
                    pos = f.tell()
                    if pos > 0:  # File has content
                        f.seek(pos - 1)
                        last_char = f.read(1)
                        if last_char != '\n':
                            needs_newline = True
            except FileNotFoundError:
                # File doesn't exist yet, no newline needed
                pass
            
            # Append to file with UTF-8 encoding
            with open(filename, 'a', encoding='utf-8') as f:
                if needs_newline:
                    f.write('\n')
                f.write(content)
            
            print(f"[AbuLang] ✓ Appended to {filename}")
            return filename
            
        except PermissionError:
            print(f"[AbuLang Error] Permission denied: Cannot write to {filename}")
            print(f"[AbuLang] Suggestion: Check file permissions or try a different location")
            return None
        except OSError as e:
            if e.errno == 28:  # No space left on device
                print(f"[AbuLang Error] Disk space full: Cannot append to {filename}")
                print(f"[AbuLang] Suggestion: Free up disk space or save to a different drive")
            elif e.errno == 22:  # Invalid argument (often bad filename)
                print(f"[AbuLang Error] Invalid filename: {filename}")
                print(f"[AbuLang] Suggestion: Avoid special characters like < > : \" / \\ | ? *")
            else:
                print(f"[AbuLang Error] Could not append to {filename}: {e}")
                print(f"[AbuLang] Suggestion: Check that the file exists and you have write permissions")
            return None
        except Exception as e:
            print(f"[AbuLang Error] Could not append to {filename}: {e}")
            print(f"[AbuLang] Suggestion: Verify the filename is valid and the path is accessible")
            return None
    
    def get_line(self, line_number, filename):
        """
        Get specific line from file
        
        Args:
            line_number: Line number (1-indexed)
            filename: Source filename or variable name
        
        Returns:
            str: Line content (without newline) or None on error
        """
        try:
            # Check if filename is a variable in context
            if filename in self.context:
                actual_filename = self.context[filename]
                if isinstance(actual_filename, str):
                    filename = actual_filename
            
            # Read file with UTF-8 encoding
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check line number bounds
            if line_number < 1 or line_number > len(lines):
                print(f"[AbuLang Error] Line {line_number} out of range (file has {len(lines)} lines)")
                return None
            
            # Return line (strip newline)
            return lines[line_number - 1].rstrip('\n')
            
        except FileNotFoundError:
            print(f"[AbuLang Error] File not found: {filename}")
            return None
        except PermissionError:
            print(f"[AbuLang Error] Permission denied: Cannot read {filename}")
            return None
        except Exception as e:
            print(f"[AbuLang Error] Could not read {filename}: {e}")
            return None
    
    def _detect_format(self, filename):
        """
        Detect format from file extension
        
        Args:
            filename: Filename with extension
            
        Returns:
            str: Detected format type
        """
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        format_map = {
            'yaml': 'yaml', 'yml': 'yaml',
            'json': 'json',
            'csv': 'csv',
            'xml': 'xml',
            'toml': 'toml',
            'ini': 'ini', 'cfg': 'ini',
            'md': 'md', 'markdown': 'md',
            'html': 'html', 'htm': 'html',
            'txt': 'txt',
            'py': 'python',
        }
        
        return format_map.get(ext, 'txt')
