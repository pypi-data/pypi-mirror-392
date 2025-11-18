"""
Format Context Manager for AbuLang Multi-Format Block System

This module provides the FormatContext class that manages format switching
and block accumulation for different file formats (YAML, JSON, CSV, etc.)
"""


class FormatContext:
    """Manages format switching and validation for multi-format blocks"""
    
    SUPPORTED_FORMATS = {
        'pythonAL': 'AbuLang mode (default)',
        'python': 'Pure Python mode',
        'yaml': 'YAML format',
        'json': 'JSON format',
        'csv': 'CSV format',
        'txt': 'Plain text',
        'xml': 'XML format',
        'toml': 'TOML format',
        'ini': 'INI/Config format',
        'md': 'Markdown format',
        'html': 'HTML format',
    }
    
    def __init__(self):
        """Initialize format context in pythonAL mode"""
        self.current_format = 'pythonAL'
        self.block_content = []
        self.in_block = False
    
    def switch_format(self, format_name):
        """
        Switch to a new format
        
        Args:
            format_name: Name of the format to switch to
            
        Raises:
            ValueError: If format_name is not supported
        """
        if format_name not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format_name}")
        
        # Track current format
        self.current_format = format_name
        
        # Clear any previous block content to maintain proper context separation
        self.block_content = []
        
        # Set in_block flag when switching to non-pythonAL formats
        # pythonAL and python modes don't accumulate blocks
        if format_name in ('pythonAL', 'python'):
            self.in_block = False
        else:
            self.in_block = True
    
    def add_line(self, line):
        """
        Add a line to current block
        
        Args:
            line: Line of text to add to the block
        """
        self.block_content.append(line)
    
    def get_block(self):
        """
        Get accumulated block content as a single string
        
        Returns:
            str: All accumulated lines joined with newlines
        """
        return '\n'.join(self.block_content)
    
    def clear_block(self):
        """
        Clear accumulated content and reset block state
        
        This is called after save_as() or append_as() to ensure
        proper context separation between format blocks.
        """
        self.block_content = []
        # Clear in_block flag to indicate we're no longer accumulating
        self.in_block = False
    
    def reset_to_pythonal(self):
        """
        Reset format context to pythonAL mode
        
        This ensures proper context separation after completing
        a format block operation (save_as or append_as).
        """
        self.current_format = 'pythonAL'
        self.block_content = []
        self.in_block = False
    
    def is_accumulating(self):
        """
        Check if currently accumulating a format block
        
        Returns:
            bool: True if in a non-pythonAL format and accumulating lines
        """
        return self.in_block and self.current_format not in ('pythonAL', 'python')
    
    def validate_block(self):
        """
        Validate current block according to its format
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        content = self.get_block()
        
        if self.current_format == 'yaml':
            return self._validate_yaml(content)
        elif self.current_format == 'json':
            return self._validate_json(content)
        elif self.current_format == 'csv':
            return self._validate_csv(content)
        elif self.current_format == 'xml':
            return self._validate_xml(content)
        elif self.current_format == 'toml':
            return self._validate_toml(content)
        elif self.current_format == 'ini':
            return self._validate_ini(content)
        elif self.current_format == 'md':
            return self._validate_markdown(content)
        elif self.current_format == 'html':
            return self._validate_html(content)
        else:
            # No validation for txt, python, pythonAL
            return True, None
    
    def _validate_yaml(self, content):
        """
        Validate YAML syntax
        
        Args:
            content: YAML content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            import yaml
            yaml.safe_load(content)
            return True, None
        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
    
    def _validate_json(self, content):
        """
        Validate JSON syntax
        
        Args:
            content: JSON content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            import json
            json.loads(content)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON syntax error: {e}"
    
    def _validate_csv(self, content):
        """
        Validate CSV format (checks for consistent column counts)
        
        Args:
            content: CSV content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            import csv
            import io
            reader = csv.reader(io.StringIO(content))
            rows = list(reader)
            
            # Check for consistent column count
            if rows:
                col_count = len(rows[0])
                for i, row in enumerate(rows[1:], 1):
                    if len(row) != col_count:
                        return False, f"CSV row {i+1} has {len(row)} columns, expected {col_count}"
            
            return True, None
        except Exception as e:
            return False, f"CSV format error: {e}"
    
    def _validate_xml(self, content):
        """
        Validate XML syntax
        
        Args:
            content: XML content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(content)
            return True, None
        except ET.ParseError as e:
            return False, f"XML syntax error: {e}"
    
    def _validate_toml(self, content):
        """
        Validate TOML syntax
        
        Args:
            content: TOML content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            import tomli
            tomli.loads(content)
            return True, None
        except ImportError:
            # tomli not installed, try tomllib (Python 3.11+)
            try:
                import tomllib
                tomllib.loads(content)
                return True, None
            except ImportError:
                return False, "TOML syntax error: tomli library not installed (pip install tomli)"
            except Exception as e:
                return False, f"TOML syntax error: {e}"
        except Exception as e:
            return False, f"TOML syntax error: {e}"
    
    def _validate_ini(self, content):
        """
        Validate INI/Config file syntax
        
        Args:
            content: INI content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            import configparser
            import io
            config = configparser.ConfigParser()
            config.read_string(content)
            return True, None
        except configparser.Error as e:
            return False, f"INI syntax error: {e}"
        except Exception as e:
            return False, f"INI format error: {e}"
    
    def _validate_markdown(self, content):
        """
        Validate Markdown syntax (basic validation)
        
        Args:
            content: Markdown content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Markdown is very permissive, so we just do basic checks
        # Check if content is not empty and is valid text
        if not content or not isinstance(content, str):
            return False, "Markdown content is empty or invalid"
        
        # Markdown doesn't have strict syntax rules, so we accept most content
        # We could add more sophisticated checks here if needed
        return True, None
    
    def _validate_html(self, content):
        """
        Validate HTML syntax
        
        Args:
            content: HTML content to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        try:
            from html.parser import HTMLParser
            
            class HTMLValidator(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.errors = []
                
                def error(self, message):
                    self.errors.append(message)
            
            parser = HTMLValidator()
            parser.feed(content)
            
            if parser.errors:
                return False, f"HTML syntax error: {parser.errors[0]}"
            
            return True, None
        except Exception as e:
            return False, f"HTML parsing error: {e}"
