"""
GUI Alias Manager for AbuLang
Provides beginner-friendly aliases for tkinter and pygame commands
"""


class GUIAliasManager:
    """
    Central registry for all GUI-related aliases in AbuLang.
    Translates friendly names to tkinter/pygame equivalents.
    """
    
    def __init__(self):
        """Initialize all alias registries"""
        self.widget_aliases = {}
        self.param_aliases = {}
        self.color_aliases = {}
        self.rgb_to_name = {}
        self.event_aliases = {}
        self.layout_aliases = {}
        self.pygame_aliases = {}
        self.module_shortcuts = {}
        
        # Initialize all registries
        self._register_widget_aliases()
        self._register_param_aliases()
        self._register_color_aliases()
        self._register_event_aliases()
        self._register_layout_aliases()
        self._register_pygame_aliases()
        self._register_module_shortcuts()
    
    def _register_widget_aliases(self):
        """Register all tkinter widget aliases"""
        self.widget_aliases = {
            # Basic widgets
            "canvas": "Canvas",
            "label": "Label",
            "btn": "Button",
            "button": "Button",
            "inputbox": "Entry",
            "ipbx": "Entry",
            "textfield": "Entry",
            "window": "Tk",
            
            # Advanced widgets
            "slider": "Scale",
            "checkbox": "Checkbutton",
            "cbx": "Checkbutton",
            "tickbox": "Checkbutton",
            "tick": "Checkbutton",
            "tickbx": "Checkbutton",
            "dropdown": "OptionMenu",
            "selector": "OptionMenu",
            "container": "Frame",
            "scrollbar": "Scrollbar",
        }
    
    def translate_widget(self, alias):
        """
        Translate a widget alias to its tkinter equivalent
        
        Args:
            alias (str): The friendly widget name
            
        Returns:
            str: The tkinter widget class name, or original if no alias found
        """
        return self.widget_aliases.get(alias.lower(), alias)

    def _register_param_aliases(self):
        """Register all parameter aliases for spacing/padding"""
        self.param_aliases = {
            # X-axis spacing
            "spacex": "padx",
            "space_x": "padx",
            "gapx": "padx",
            "gap_x": "padx",
            "marginx": "padx",
            "margin_x": "padx",
            
            # Y-axis spacing
            "spacey": "pady",
            "space_y": "pady",
            "gapy": "pady",
            "gap_y": "pady",
            "marginy": "pady",
            "margin_y": "pady",
        }
    
    def translate_param(self, alias):
        """
        Translate a parameter alias to its tkinter equivalent
        
        Args:
            alias (str): The friendly parameter name
            
        Returns:
            str: The tkinter parameter name, or original if no alias found
        """
        return self.param_aliases.get(alias.lower(), alias)

    def _register_color_aliases(self):
        """Register all color name to RGB mappings"""
        self.color_aliases = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "yellow": (255, 255, 0),
        }
        
        # Create reverse lookup dictionary
        self.rgb_to_name = {v: k for k, v in self.color_aliases.items()}
    
    def translate_color(self, alias):
        """
        Translate a color name to its RGB tuple
        
        Args:
            alias (str): The color name
            
        Returns:
            tuple: RGB tuple (r, g, b), or original if no alias found
        """
        return self.color_aliases.get(alias.lower(), alias)

    def get_hex_from_object(self, obj):
        """
        Get RGB tuple from object's hex attribute
        
        Args:
            obj: Object with .hex attribute
            
        Returns:
            tuple: RGB tuple (r, g, b)
        """
        if hasattr(obj, 'hex'):
            hex_value = obj.hex
            # If hex is already an RGB tuple, return it
            if isinstance(hex_value, tuple) and len(hex_value) == 3:
                return hex_value
            # If hex is a string like "#RRGGBB", convert it
            if isinstance(hex_value, str) and hex_value.startswith('#'):
                hex_value = hex_value.lstrip('#')
                return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
        return None
    
    def get_color_name_from_object(self, obj):
        """
        Get color name from object's color/colour attribute
        
        Args:
            obj: Object with .color or .colour attribute
            
        Returns:
            str: Color name, or None if not found
        """
        # Try .color attribute
        if hasattr(obj, 'color'):
            color_value = obj.color
            # If it's already a name, return it
            if isinstance(color_value, str):
                return color_value
            # If it's an RGB tuple, look up the name
            if isinstance(color_value, tuple) and len(color_value) == 3:
                return self.rgb_to_name.get(color_value, None)
        
        # Try .colour attribute (British spelling)
        if hasattr(obj, 'colour'):
            colour_value = obj.colour
            # If it's already a name, return it
            if isinstance(colour_value, str):
                return colour_value
            # If it's an RGB tuple, look up the name
            if isinstance(colour_value, tuple) and len(colour_value) == 3:
                return self.rgb_to_name.get(colour_value, None)
        
        return None

    def get_coords(self, canvas, obj, full=False):
        """
        Get coordinates of a canvas object with labeled corners
        
        Args:
            canvas: Canvas widget containing the object
            obj: Canvas object ID
            full (bool): If True, return all corner labels (UL, UR, DL, DR)
                        If False, return only bounding box coordinates
        
        Returns:
            dict: Dictionary with labeled coordinates
                  {'UL': (x1, y1), 'UR': (x2, y1), 'DL': (x1, y2), 'DR': (x2, y2)}
        
        Example:
            >>> coords = get_coords(canvas, shape_id)
            >>> print(coords['UL'])  # Upper Left corner
            >>> print(coords['DR'])  # Down Right corner
        """
        # Get bounding box coordinates from canvas
        bbox = canvas.coords(obj)
        
        if len(bbox) >= 4:
            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
        else:
            raise ValueError(f"Object {obj} does not have valid bounding box coordinates")
        
        # Return labeled coordinates
        return {
            'UL': (x1, y1),  # Upper Left
            'UR': (x2, y1),  # Upper Right
            'DL': (x1, y2),  # Down Left
            'DR': (x2, y2),  # Down Right
        }

    def _register_event_aliases(self):
        """Register all event handling aliases"""
        self.event_aliases = {
            "onclick": "<Button-1>",
            "onkey": "<Key>",
            "onhover": "<Enter>",
            "onleave": "<Leave>",
        }
    
    def translate_event(self, event_str):
        """
        Translate event aliases including dynamic key bindings
        
        Supports both predefined aliases and dynamic "on<key>" pattern.
        
        Args:
            event_str (str): The friendly event name (e.g., "onclick", "ona", "onspace")
            
        Returns:
            str: The tkinter bind format (e.g., "<Button-1>", "<a>", "<space>")
        
        Examples:
            >>> translate_event("onclick")
            '<Button-1>'
            >>> translate_event("ona")
            '<a>'
            >>> translate_event("onspace")
            '<space>'
            >>> translate_event("onenter")
            '<enter>'
        """
        # Check if it's a predefined alias
        if event_str.lower() in self.event_aliases:
            return self.event_aliases[event_str.lower()]
        
        # Handle dynamic "on<key>" pattern
        if event_str.lower().startswith("on") and len(event_str) > 2:
            # Extract the key name (everything after "on")
            key = event_str[2:].lower()
            
            # Handle special key names that need specific formatting
            special_keys = {
                "space": "space",
                "enter": "Return",
                "return": "Return",
                "escape": "Escape",
                "esc": "Escape",
                "tab": "Tab",
                "backspace": "BackSpace",
                "delete": "Delete",
                "del": "Delete",
                "up": "Up",
                "down": "Down",
                "left": "Left",
                "right": "Right",
                "shift": "Shift_L",
                "ctrl": "Control_L",
                "control": "Control_L",
                "alt": "Alt_L",
            }
            
            # Use special key mapping if available, otherwise use the key as-is
            key_name = special_keys.get(key, key)
            
            return f"<{key_name}>"
        
        # If no pattern matches, return the original string
        return event_str
    
    def _register_layout_aliases(self):
        """Register all layout manager aliases"""
        # NOTE: pack, grid, and place are standard tkinter methods
        # They're already clear and intuitive, so no aliases needed
        self.layout_aliases = {
            # Empty - tkinter layout managers don't need aliases
        }
    
    def translate_layout(self, alias):
        """
        Translate a layout manager alias to its tkinter equivalent
        
        Args:
            alias (str): The friendly layout manager name
            
        Returns:
            str: The tkinter layout manager name, or original if no alias found
        
        Examples:
            >>> translate_layout("place")
            'pack'
            >>> translate_layout("arrange")
            'grid'
            >>> translate_layout("position")
            'place'
            >>> translate_layout("show_it")
            'pack'
        """
        return self.layout_aliases.get(alias.lower(), alias)
    
    def translate_pygame(self, alias):
        """
        Translate a pygame alias to its pygame equivalent
        
        Args:
            alias (str): The friendly pygame function name
            
        Returns:
            str: The pygame function name, or original if no alias found
        
        Examples:
            >>> translate_pygame("screen")
            'init'
            >>> translate_pygame("setup")
            'init'
            >>> translate_pygame("start")
            'init'
            >>> translate_pygame("makescreen")
            'set_mode'
            >>> translate_pygame("refresh")
            'flip'
            >>> translate_pygame("update")
            'update'
            >>> translate_pygame("draw")
            'blit'
            >>> translate_pygame("fill")
            'fill'
        """
        return self.pygame_aliases.get(alias.lower(), alias)
    
    def _register_pygame_aliases(self):
        """Register all pygame aliases"""
        self.pygame_aliases = {
            # Initialization aliases
            "screen": "init",
            "setup": "init",
            "start": "init",
            
            # Display aliases
            "makescreen": "set_mode",
            "refresh": "flip",
            "update": "update",
            
            # Drawing aliases
            "draw": "blit",
            "fill": "fill",
        }
    
    def _register_module_shortcuts(self):
        """Register module import shortcuts for auto-aliasing"""
        self.module_shortcuts = {
            "arrow": {
                "module": "turtle",
                "auto_aliases": ["ar"],
                "description": "Turtle graphics library"
            },
            "DISPLAY": {
                "module": "pygame",
                "auto_aliases": ["ds"],
                "description": "Pygame game development library"
            },
            "UI": {
                "module": "tkinter",
                "auto_aliases": ["ui"],
                "description": "Tkinter GUI library"
            },
        }
        
        # Initialize help categories
        self._register_help_categories()
    
    def _register_help_categories(self):
        """Register all help categories for GUI aliases"""
        self.help_categories = {
            "widgets": {
                "description": "GUI widget aliases for tkinter",
                "aliases": {
                    "canvas": {"target": "Canvas", "desc": "Drawing surface for shapes and graphics"},
                    "label": {"target": "Label", "desc": "Display text on screen"},
                    "btn/button": {"target": "Button", "desc": "Create a clickable button"},
                    "inputbox/ipbx": {"target": "Entry", "desc": "Text input field"},
                    "textfield": {"target": "Entry", "desc": "Text input field (alias)"},
                    "window": {"target": "Tk", "desc": "Create main application window"},
                    "slider": {"target": "Scale", "desc": "Slider control for numeric input"},
                    "checkbox/cbx": {"target": "Checkbutton", "desc": "Checkbox for yes/no options"},
                    "tickbox/tick": {"target": "Checkbutton", "desc": "Checkbox (alternative names)"},
                    "dropdown": {"target": "OptionMenu", "desc": "Dropdown selection menu"},
                    "selector": {"target": "OptionMenu", "desc": "Selection menu (alias)"},
                    "container": {"target": "Frame", "desc": "Container for grouping widgets"},
                    "scrollbar": {"target": "Scrollbar", "desc": "Scrollbar for scrolling content"},
                },
                "examples": [
                    "my_btn = button(window, text='Click Me')",
                    "my_label = label(window, text='Hello World')",
                    "my_input = inputbox(window)",
                    "my_canvas = canvas(window, width=400, height=300)",
                ]
            },
            "colors": {
                "description": "Color name aliases (converts to RGB/hex)",
                "aliases": {
                    "red": {"target": "(255, 0, 0)", "desc": "Pure red color"},
                    "green": {"target": "(0, 255, 0)", "desc": "Pure green color"},
                    "blue": {"target": "(0, 0, 255)", "desc": "Pure blue color"},
                    "white": {"target": "(255, 255, 255)", "desc": "White color"},
                    "black": {"target": "(0, 0, 0)", "desc": "Black color"},
                    "yellow": {"target": "(255, 255, 0)", "desc": "Yellow color"},
                },
                "helpers": {
                    "object.hex": "Get RGB tuple from object",
                    "object.color": "Get color name from object",
                    "object.colour": "Get color name from object (British spelling)",
                },
                "examples": [
                    "def_box(canvas, 'rectangle', 10, 10, 100, 100, color='red')",
                    "def_circle(canvas, 50, 50, 25, color='blue')",
                    "my_label = label(window, bg='yellow', fg='black')",
                ]
            },
            "events": {
                "description": "Event handling aliases for user interactions",
                "aliases": {
                    "onclick": {"target": "<Button-1>", "desc": "Mouse click event"},
                    "onkey": {"target": "<Key>", "desc": "Any key press event"},
                    "onhover": {"target": "<Enter>", "desc": "Mouse enters widget"},
                    "onleave": {"target": "<Leave>", "desc": "Mouse leaves widget"},
                    "on<key>": {"target": "<key>", "desc": "Dynamic key binding (ona, onb, onspace, etc.)"},
                },
                "examples": [
                    "canvas.bind(onclick, my_function)",
                    "window.bind(ona, handle_a_key)",
                    "window.bind(onspace, jump_function)",
                    "button.bind(onhover, highlight)",
                ]
            },
            "layout": {
                "description": "Layout manager aliases for positioning widgets",
                "aliases": {
                    "place": {"target": "pack()", "desc": "Simple automatic layout"},
                    "arrange": {"target": "grid()", "desc": "Grid-based layout"},
                    "position": {"target": "place()", "desc": "Absolute positioning"},
                    "show_it": {"target": "pack()", "desc": "Display widget (note: 'show' is print)"},
                },
                "parameters": {
                    "spacex/space_x": "Horizontal spacing (padx)",
                    "spacey/space_y": "Vertical spacing (pady)",
                    "gapx/gap_x": "Horizontal gap (padx)",
                    "gapy/gap_y": "Vertical gap (pady)",
                    "marginx/margin_x": "Horizontal margin (padx)",
                    "marginy/margin_y": "Vertical margin (pady)",
                },
                "examples": [
                    "my_button.place()",
                    "my_label.arrange(row=0, column=0)",
                    "my_input.position(x=50, y=100)",
                    "my_button.pack(spacex=10, spacey=5)",
                ]
            },
            "shapes": {
                "description": "Shape drawing functions for canvas",
                "aliases": {
                    "def_box": {"target": "create_rectangle/oval", "desc": "Draw rectangle or oval"},
                    "def_circle": {"target": "create_oval", "desc": "Draw circle with hitbox"},
                    "coords/coordsfull": {"target": "get_coords()", "desc": "Get labeled coordinates (UL, UR, DL, DR)"},
                },
                "examples": [
                    "box_id = def_box(canvas, 'rectangle', 10, 10, 100, 100, color='red')",
                    "oval_id = def_box(canvas, 'oval', 50, 50, 150, 150, color='blue')",
                    "circle = def_circle(canvas, 100, 100, 50, color='green')",
                    "coords = get_coords(canvas, shape_id)",
                    "print(coords['UL'])  # Upper Left corner",
                ]
            },
            "ui": {
                "description": "Tkinter (UI) library aliases and shortcuts",
                "info": "Import with: libra UI (auto-creates 'ui' alias)",
                "aliases": {
                    "UI": {"target": "tkinter", "desc": "Main tkinter library"},
                    "ui": {"target": "tkinter", "desc": "Auto-alias for tkinter"},
                },
                "common_usage": [
                    "libra UI  # Imports tkinter, creates 'ui' alias",
                    "window = UI.Tk()  # or ui.Tk()",
                    "button = ui.Button(window, text='Click')",
                    "canvas = ui.Canvas(window, width=400, height=300)",
                ],
                "see_also": "Type 'help widgets' for widget aliases"
            },
            "display": {
                "description": "Pygame (DISPLAY) library aliases and shortcuts",
                "info": "Import with: libra DISPLAY (auto-creates 'ds' alias)",
                "aliases": {
                    "DISPLAY": {"target": "pygame", "desc": "Main pygame library"},
                    "ds": {"target": "pygame", "desc": "Auto-alias for pygame"},
                    "screen/setup/start": {"target": "init()", "desc": "Initialize pygame"},
                    "makescreen": {"target": "set_mode()", "desc": "Create display window"},
                    "refresh": {"target": "flip()", "desc": "Update display"},
                    "update": {"target": "update()", "desc": "Update portions of display"},
                    "draw": {"target": "blit()", "desc": "Draw surface on screen"},
                    "fill": {"target": "fill()", "desc": "Fill surface with color"},
                },
                "common_usage": [
                    "libra DISPLAY  # Imports pygame, creates 'ds' alias",
                    "DISPLAY.screen()  # or ds.screen() - initialize",
                    "window = ds.makescreen((800, 600))",
                    "window.fill(black)",
                    "ds.refresh()  # Update display",
                ],
                "see_also": "Type 'help colors' for color aliases"
            },
            "arrow": {
                "description": "Turtle (arrow) library aliases and shortcuts",
                "info": "Import with: libra arrow (auto-creates 'ar' alias)",
                "aliases": {
                    "arrow": {"target": "turtle", "desc": "Main turtle graphics library"},
                    "ar": {"target": "turtle", "desc": "Auto-alias for turtle"},
                },
                "common_usage": [
                    "libra arrow  # Imports turtle, creates 'ar' alias",
                    "arrow.forward(100)  # or ar.forward(100)",
                    "ar.left(90)",
                    "ar.circle(50)",
                ],
            },
        }
    
    def get_help_category(self, category):
        """
        Get help information for a specific category
        
        Args:
            category (str): The help category name
            
        Returns:
            dict: Help information for the category, or None if not found
        """
        return self.help_categories.get(category.lower(), None)
    
    def get_all_help_categories(self):
        """
        Get list of all available help categories
        
        Returns:
            list: List of category names
        """
        return list(self.help_categories.keys())
    
    def get_auto_aliases(self, module_name):
        """
        Get auto-aliases for a module name
        
        Args:
            module_name (str): The module name (e.g., "arrow", "DISPLAY", "UI")
            
        Returns:
            list: List of auto-alias names, or empty list if none found
        
        Examples:
            >>> get_auto_aliases("arrow")
            ['ar']
            >>> get_auto_aliases("DISPLAY")
            ['ds']
            >>> get_auto_aliases("UI")
            ['ui']
        """
        if module_name in self.module_shortcuts:
            return self.module_shortcuts[module_name].get("auto_aliases", [])
        return []
    
    def get_real_module_name(self, alias):
        """
        Get the real Python module name from an AbuLang alias
        
        Args:
            alias (str): The AbuLang module alias (e.g., "arrow", "DISPLAY", "UI")
            
        Returns:
            str: The real Python module name, or the original alias if not found
        
        Examples:
            >>> get_real_module_name("arrow")
            'turtle'
            >>> get_real_module_name("DISPLAY")
            'pygame'
            >>> get_real_module_name("UI")
            'tkinter'
        """
        if alias in self.module_shortcuts:
            return self.module_shortcuts[alias]["module"]
        return alias
    
    def translate_syntax_enhancements(self, line):
        """
        Translate syntax enhancements like =:, is, pos_value, neg_value, Always True
        
        This method handles:
        1. =: operator (assign and compare)
        2. "is" for assignment
        3. pos_value/neg_value checks
        4. "Always True" conditions
        5. Permanent assignment with "always"
        
        Args:
            line (str): The line of code to translate
            
        Returns:
            str: The translated line with syntax enhancements applied
        """
        import re
        
        # Preserve string literals
        strings = []
        def save_string(match):
            strings.append(match.group(0))
            return f"__STRING_{len(strings)-1}__"
        
        line = re.sub(r'"[^"]*"', save_string, line)
        line = re.sub(r"'[^']*'", save_string, line)
        
        # 1. Handle =: operator (assign and compare)
        # Pattern: variable =: value comparison_var
        # Example: x =: 6y -> assign x=6, then compare x to y
        assign_compare_match = re.search(r'(\w+)\s*=:\s*(\d+)\s*(\w+)', line)
        if assign_compare_match:
            var = assign_compare_match.group(1)
            value = assign_compare_match.group(2)
            compare_var = assign_compare_match.group(3)
            
            # This needs to be handled at runtime, so we'll create a special marker
            # The runner will need to handle this specially
            replacement = f'{var} = {value}  # __COMPARE_TO_{compare_var}__'
            line = line[:assign_compare_match.start()] + replacement + line[assign_compare_match.end():]
        
        # 2. Handle "Always True" conditions (case insensitive)
        # Pattern: if Always True: or while Always True:
        line = re.sub(r'\bif\s+always\s+true\s*:', 'if True:', line, flags=re.IGNORECASE)
        line = re.sub(r'\bwhile\s+always\s+true\s*:', 'while True:', line, flags=re.IGNORECASE)
        
        # Handle actual always-true conditions like "if 5=5:" -> "if 5==5:"
        # Replace single = with == in conditionals (but not in assignments)
        def fix_conditional_equals(match):
            condition = match.group(1)
            # Replace single = with == in the condition
            fixed_condition = re.sub(r'(\d+|[a-zA-Z_]\w*)\s*=\s*(\d+|[a-zA-Z_]\w*)', r'\1 == \2', condition)
            return f'if {fixed_condition}:'
        
        line = re.sub(r'if\s+([^:]+):', fix_conditional_equals, line)
        
        # 3. Handle pos_value and neg_value checks
        # Pattern: "has pos_value" or "has positive_value" -> "> 0"
        line = re.sub(r'\bhas\s+pos(?:itive)?_value\b', '> 0', line, flags=re.IGNORECASE)
        line = re.sub(r'\bhas\s+neg(?:ative)?_value\b', '< 0', line, flags=re.IGNORECASE)
        
        # Pattern: "variable value is pos_value" or "variable value is neg_value"
        # This checks against stored type metadata
        # We'll mark these for runtime checking with a special marker
        value_type_check = re.search(r'(\w+)\s+value\s+is\s+(pos_value|neg_value)', line, flags=re.IGNORECASE)
        if value_type_check:
            var = value_type_check.group(1)
            type_check = value_type_check.group(2).lower()
            # Replace with a runtime check marker
            replacement = f'__CHECK_VALUE_TYPE__({var}, "{type_check}")'
            line = line[:value_type_check.start()] + replacement + line[value_type_check.end():]
        
        # Pattern: "is pos_value" or "is neg_value" (without "value" keyword) -> "> 0" or "< 0"
        line = re.sub(r'\bis\s+pos(?:itive)?_value\b', '> 0', line, flags=re.IGNORECASE)
        line = re.sub(r'\bis\s+neg(?:ative)?_value\b', '< 0', line, flags=re.IGNORECASE)
        
        # 4. Handle flexible assignment with "is"
        # Pattern: variable is value (not in conditionals)
        # We need to be careful not to replace "is" in comparisons
        # Only replace if it's not after "if" or "while" and not followed by comparison operators
        if not line.strip().startswith('if ') and not line.strip().startswith('while '):
            # Check if this looks like an assignment (not a comparison)
            # Assignment: x is 5, name is "John"
            # Comparison: if x is 5 (should stay as is for identity check)
            is_assignment_match = re.search(r'^(\s*)(\w+)\s+is\s+(.+)$', line)
            if is_assignment_match:
                indent = is_assignment_match.group(1)
                var = is_assignment_match.group(2)
                value = is_assignment_match.group(3)
                line = f'{indent}{var} = {value}'
        
        # 5. Handle permanent assignment with "always"
        # Pattern: variable = always value or variable is always value
        # This creates a constant that should not be reassigned
        always_match = re.search(r'(\w+)\s+(?:=|is)\s+always\s+(.+)', line)
        if always_match:
            var = always_match.group(1)
            value = always_match.group(2)
            # Mark as constant with a comment for now
            # A more sophisticated implementation would track constants
            line = f'{var} = {value}  # __CONSTANT__'
        
        # Restore string literals
        for i, s in enumerate(strings):
            line = line.replace(f"__STRING_{i}__", s)
        
        return line
    
    def translate_line(self, line):
        """
        Translate all GUI aliases in a line of code
        
        This method processes a line through multiple translation stages:
        1. Syntax enhancements (=:, is, pos_value, Always True, etc.)
        2. Widget name translation (btn -> Button, canvas -> Canvas, etc.)
        3. Parameter name translation (spacex -> padx, gapy -> pady, etc.)
        4. Color name translation (red -> #ff0000, blue -> #0000ff, etc.)
        5. Event name translation (onclick -> <Button-1>, ona -> <a>, etc.)
        6. Layout manager translation (place -> pack, arrange -> grid, etc.)
        7. Pygame function translation (screen -> init, refresh -> flip, etc.)
        
        String literals are preserved during translation to avoid modifying
        text content that should remain unchanged.
        
        Args:
            line (str): The line of code to translate
            
        Returns:
            str: The translated line with all aliases replaced
        
        Examples:
            >>> translate_line("my_btn = btn(window, text='Click')")
            "my_btn = Button(window, text='Click')"
            
            >>> translate_line("canvas.bind(onclick, handler)")
            "canvas.bind(<Button-1>, handler)"
            
            >>> translate_line("label.pack(spacex=10, spacey=5)")
            "label.pack(padx=10, pady=5)"
        """
        import re
        
        # Step 0: Apply syntax enhancements first
        line = self.translate_syntax_enhancements(line)
        
        # Step 1: Preserve string literals
        # We need to protect strings from translation
        strings = []
        def save_string(match):
            strings.append(match.group(0))
            return f"__STRING_{len(strings)-1}__"
        
        # Save all strings (both single and double quoted)
        line = re.sub(r'"[^"]*"', save_string, line)
        line = re.sub(r"'[^']*'", save_string, line)
        
        # Step 2: Translate widget names ONLY when used with ui. prefix
        # Don't translate variable names that happen to match widget names
        # Example: ui.Button() -> ui.Button() (no change, already correct)
        # Example: window.configure() -> window.configure() (no change, it's a variable)
        # Widget aliases are only useful for AbuLang-style code, not Python code
        # Since AbuLang supports normal Python, we skip widget translation
        # Users can use: ui.Button(), ui.Label(), etc. directly
        
        # Step 3: Translate parameter names
        # These typically appear as keyword arguments (param=value)
        for alias, target in self.param_aliases.items():
            # Match parameter names (with = after them or as standalone)
            pattern = r'\b' + re.escape(alias) + r'\b'
            line = re.sub(pattern, target, line, flags=re.IGNORECASE)
        
        # Step 4: Translate color names
        # Look for color names in common contexts (color=, fill=, etc.)
        for color_name, rgb_value in self.color_aliases.items():
            # Convert RGB to hex format
            hex_color = '#%02x%02x%02x' % rgb_value
            
            # Match color names in various contexts
            # Pattern: color_name as a standalone word (not in strings)
            pattern = r'\b' + re.escape(color_name) + r'\b'
            
            # Only replace if it looks like a color context
            # (after =, in function calls, etc.)
            def replace_color(match):
                # Get the context before the match
                start = max(0, match.start() - 10)
                context = line[start:match.start()]
                # Check if it's in a color-related context
                if any(keyword in context for keyword in ['color', 'fill', 'bg', 'fg', 'background', 'foreground']):
                    return f'"{hex_color}"'
                return match.group(0)
            
            line = re.sub(pattern, replace_color, line, flags=re.IGNORECASE)
        
        # Step 5: Translate event names
        # These typically appear in bind() calls or event handlers
        for alias, target in self.event_aliases.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            line = re.sub(pattern, f'"{target}"', line, flags=re.IGNORECASE)
        
        # Handle dynamic "on<key>" pattern (ona, onb, onspace, etc.)
        # Match pattern: on followed by letters (not in strings)
        def translate_dynamic_event(match):
            event_str = match.group(0)
            if event_str.lower().startswith("on") and len(event_str) > 2:
                translated = self.translate_event(event_str)
                if translated != event_str:
                    return f'"{translated}"'
            return event_str
        
        line = re.sub(r'\bon[a-z]+\b', translate_dynamic_event, line, flags=re.IGNORECASE)
        
        # Step 6: Translate layout manager names
        # These typically appear as method calls (.place(), .arrange(), etc.)
        for alias, target in self.layout_aliases.items():
            # Match as method calls or standalone
            pattern = r'\b' + re.escape(alias) + r'\b'
            line = re.sub(pattern, target, line, flags=re.IGNORECASE)
        
        # Step 7: Translate pygame function names
        # These typically appear in pygame module calls (pygame.screen(), ds.refresh(), etc.)
        for alias, target in self.pygame_aliases.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            line = re.sub(pattern, target, line, flags=re.IGNORECASE)
        
        # Step 8: Restore string literals
        for i, s in enumerate(strings):
            line = line.replace(f"__STRING_{i}__", s)
        
        return line
    
    def def_box(self, canvas, shape_type, x1, y1, x2, y2, color="black", **kwargs):
        """
        Simplified shape drawing for tkinter Canvas
        
        Args:
            canvas: Canvas widget
            shape_type (str): "rectangle" or "oval"
            x1 (int/float): Top-left x coordinate
            y1 (int/float): Top-left y coordinate
            x2 (int/float): Bottom-right x coordinate
            y2 (int/float): Bottom-right y coordinate
            color (str/tuple): Color name or RGB tuple
            **kwargs: Additional canvas options (outline, width, etc.)
        
        Returns:
            int: Shape ID for reference
        """
        # Translate color name to RGB/hex if it's a string alias
        if isinstance(color, str):
            color_value = self.translate_color(color)
            # Convert RGB tuple to hex format for tkinter
            if isinstance(color_value, tuple) and len(color_value) == 3:
                color_value = '#%02x%02x%02x' % color_value
        elif isinstance(color, tuple) and len(color) == 3:
            # If color is already an RGB tuple, convert to hex
            color_value = '#%02x%02x%02x' % color
        else:
            color_value = color
        
        # Create the shape based on type
        if shape_type.lower() == "rectangle":
            return canvas.create_rectangle(x1, y1, x2, y2, fill=color_value, **kwargs)
        elif shape_type.lower() == "oval":
            return canvas.create_oval(x1, y1, x2, y2, fill=color_value, **kwargs)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}. Use 'rectangle' or 'oval'.")
    
    def def_circle(self, canvas, center_x, center_y, radius, color="black", **kwargs):
        """
        Draw a circle with hitbox detection
        
        Args:
            canvas: Canvas widget
            center_x (int/float): Center x coordinate
            center_y (int/float): Center y coordinate
            radius (int/float): Circle radius
            color (str/tuple): Color name or RGB tuple
            **kwargs: Additional canvas options (outline, width, etc.)
        
        Returns:
            dict: Dictionary with 'id', 'center', 'radius', and 'hitbox' info
        """
        # Calculate bounding box from center and radius
        x1 = center_x - radius
        y1 = center_y - radius
        x2 = center_x + radius
        y2 = center_y + radius
        
        # Translate color name to RGB/hex if it's a string alias
        if isinstance(color, str):
            color_value = self.translate_color(color)
            # Convert RGB tuple to hex format for tkinter
            if isinstance(color_value, tuple) and len(color_value) == 3:
                color_value = '#%02x%02x%02x' % color_value
        elif isinstance(color, tuple) and len(color) == 3:
            # If color is already an RGB tuple, convert to hex
            color_value = '#%02x%02x%02x' % color
        else:
            color_value = color
        
        # Create the circle using create_oval
        circle_id = canvas.create_oval(x1, y1, x2, y2, fill=color_value, **kwargs)
        
        # Return comprehensive info including hitbox
        return {
            'id': circle_id,
            'center': (center_x, center_y),
            'radius': radius,
            'hitbox': {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
        }


# Standalone helper functions for easy access
_gui_manager = GUIAliasManager()


def def_box(canvas, shape_type, x1, y1, x2, y2, color="black", **kwargs):
    """
    Simplified shape drawing for tkinter Canvas
    
    Args:
        canvas: Canvas widget
        shape_type (str): "rectangle" or "oval"
        x1 (int/float): Top-left x coordinate
        y1 (int/float): Top-left y coordinate
        x2 (int/float): Bottom-right x coordinate
        y2 (int/float): Bottom-right y coordinate
        color (str/tuple): Color name or RGB tuple
        **kwargs: Additional canvas options (outline, width, etc.)
    
    Returns:
        int: Shape ID for reference
    
    Example:
        >>> def_box(canvas, "rectangle", 10, 10, 100, 100, color="red")
        >>> def_box(canvas, "oval", 50, 50, 150, 150, color="blue", outline="black")
    """
    return _gui_manager.def_box(canvas, shape_type, x1, y1, x2, y2, color, **kwargs)


def def_circle(canvas, center_x, center_y, radius, color="black", **kwargs):
    """
    Draw a circle with hitbox detection
    
    Args:
        canvas: Canvas widget
        center_x (int/float): Center x coordinate
        center_y (int/float): Center y coordinate
        radius (int/float): Circle radius
        color (str/tuple): Color name or RGB tuple
        **kwargs: Additional canvas options (outline, width, etc.)
    
    Returns:
        dict: Dictionary with 'id', 'center', 'radius', and 'hitbox' info
    
    Example:
        >>> circle = def_circle(canvas, 100, 100, 50, color="green")
        >>> print(circle['id'])  # Canvas object ID
        >>> print(circle['center'])  # (100, 100)
        >>> print(circle['hitbox'])  # {'x1': 50, 'y1': 50, 'x2': 150, 'y2': 150}
    """
    return _gui_manager.def_circle(canvas, center_x, center_y, radius, color, **kwargs)


def get_coords(canvas, obj, full=False):
    """
    Get coordinates of a canvas object with labeled corners
    
    Args:
        canvas: Canvas widget containing the object
        obj: Canvas object ID
        full (bool): If True, return all corner labels (UL, UR, DL, DR)
                    If False, return only bounding box coordinates
    
    Returns:
        dict: Dictionary with labeled coordinates
              {'UL': (x1, y1), 'UR': (x2, y1), 'DL': (x1, y2), 'DR': (x2, y2)}
    
    Example:
        >>> coords = get_coords(canvas, shape_id)
        >>> print(coords['UL'])  # Upper Left: (10, 10)
        >>> print(coords['UR'])  # Upper Right: (100, 10)
        >>> print(coords['DL'])  # Down Left: (10, 100)
        >>> print(coords['DR'])  # Down Right: (100, 100)
        
        >>> # Access specific corners
        >>> upper_left = coords['UL']
        >>> down_right = coords['DR']
    """
    return _gui_manager.get_coords(canvas, obj, full)
