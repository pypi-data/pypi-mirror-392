"""
AbuLang IDLE GUI - Full Python IDLE clone with file editor
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font
import sys
import os
from .runner import AbuRunner


class AbuIDLEGUI:
    """Full IDLE-like GUI for AbuLang"""

    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("AbuLang IDLE")
        self.root.geometry("900x700")
        
        self.runner = AbuRunner()
        self.current_file = None
        self.file_modified = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_keybindings()

    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Paned window for editor and shell
        paned = tk.PanedWindow(main_frame, orient=tk.VERTICAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # === EDITOR FRAME ===
        editor_frame = tk.Frame(paned)
        paned.add(editor_frame, height=400)
        
        # Editor label
        editor_label = tk.Label(editor_frame, text="Editor", bg="lightgray", font=("Arial", 10, "bold"))
        editor_label.pack(side=tk.TOP, fill=tk.X)
        
        # Editor with line numbers
        editor_container = tk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_container, width=4, bg="lightgray", fg="black", 
                                     font=("Courier", 10), state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor text
        self.editor = scrolledtext.ScrolledText(editor_container, wrap=tk.WORD, 
                                                font=("Courier", 10), undo=True)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<Control-s>", lambda e: self.save_file())
        self.editor.bind("<Control-o>", lambda e: self.open_file())
        self.editor.bind("<Control-n>", lambda e: self.new_file())
        self.editor.bind("<F5>", lambda e: self.run_code())
        
        # === SHELL FRAME ===
        shell_frame = tk.Frame(paned)
        paned.add(shell_frame, height=300)
        
        # Shell label
        shell_label = tk.Label(shell_frame, text="Shell", bg="lightgray", font=("Arial", 10, "bold"))
        shell_label.pack(side=tk.TOP, fill=tk.X)
        
        # Shell output
        self.shell_output = scrolledtext.ScrolledText(shell_frame, wrap=tk.WORD, 
                                                      font=("Courier", 10), state=tk.DISABLED,
                                                      bg="black", fg="white")
        self.shell_output.pack(fill=tk.BOTH, expand=True)
        
        # Shell input
        input_frame = tk.Frame(shell_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(input_frame, text=">>>", font=("Courier", 10)).pack(side=tk.LEFT)
        
        self.shell_input = tk.Entry(input_frame, font=("Courier", 10))
        self.shell_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.shell_input.bind("<Return>", self.execute_shell_command)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bg="lightgray", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Print welcome message
        self.print_shell("AbuLang IDLE v3.0.0\n")
        self.print_shell("Type 'help' for help, 'exit' to quit\n")
        self.print_shell("Press F5 to run code\n\n")

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.editor.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.editor.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.editor.event_generate("<<Paste>>"))
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="Clear Shell", command=self.clear_shell)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_keybindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-z>", lambda e: self.editor.edit_undo())
        self.root.bind("<Control-y>", lambda e: self.editor.edit_redo())

    def update_line_numbers(self, event=None):
        """Update line numbers"""
        try:
            content = self.editor.get("1.0", tk.END)
            lines = content.count("\n")
            line_numbers_text = "\n".join(str(i) for i in range(1, lines + 1))
            
            self.line_numbers.config(state=tk.NORMAL)
            self.line_numbers.delete("1.0", tk.END)
            self.line_numbers.insert("1.0", line_numbers_text)
            self.line_numbers.config(state=tk.DISABLED)
            
            self.file_modified = True
            self.update_title()
        except Exception as e:
            pass  # Silently ignore line number update errors

    def print_shell(self, text):
        """Print text to shell output"""
        self.shell_output.config(state=tk.NORMAL)
        self.shell_output.insert(tk.END, text)
        self.shell_output.see(tk.END)
        self.shell_output.config(state=tk.DISABLED)

    def execute_shell_command(self, event=None):
        """Execute command from shell input"""
        command = self.shell_input.get()
        self.shell_input.delete(0, tk.END)
        
        if not command.strip():
            return
        
        self.print_shell(f">>> {command}\n")
        
        if command.lower() == "exit":
            self.root.quit()
            return
        
        if command.lower() == "clear":
            self.clear_shell()
            return
        
        try:
            # Redirect stdout to capture print output
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.runner.execute_line(command)
            
            # Get captured output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            if output:
                self.print_shell(output)
        except Exception as e:
            sys.stdout = old_stdout
            self.print_shell(f"[Error] {e}\n")
        
        self.print_shell("\n")

    def run_code(self):
        """Run code from editor"""
        code = self.editor.get("1.0", tk.END)
        
        if not code.strip():
            messagebox.showwarning("Empty", "No code to run")
            return
        
        self.print_shell("=" * 60 + "\n")
        self.print_shell("Running code...\n")
        self.print_shell("=" * 60 + "\n")
        
        try:
            # Redirect stdout to capture print output
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                self.runner.run(code)
            finally:
                # Get captured output
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
            
            if output:
                self.print_shell(output)
        except Exception as e:
            sys.stdout = old_stdout
            self.print_shell(f"[Error] {type(e).__name__}: {e}\n")
            import traceback
            self.print_shell(traceback.format_exc())
        
        self.print_shell("=" * 60 + "\n\n")

    def clear_shell(self):
        """Clear shell output"""
        self.shell_output.config(state=tk.NORMAL)
        self.shell_output.delete("1.0", tk.END)
        self.shell_output.config(state=tk.DISABLED)

    def new_file(self):
        """Create new file"""
        if self.file_modified:
            if messagebox.askyesno("Save", "Save changes before creating new file?"):
                self.save_file()
        
        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.file_modified = False
        self.update_title()
        self.update_line_numbers()

    def open_file(self):
        """Open file"""
        filename = filedialog.askopenfilename(
            filetypes=[("AbuLang files", "*.abu"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
                self.current_file = filename
                self.file_modified = False
                self.update_title()
                self.update_line_numbers()
                self.status_bar.config(text=f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """Save file"""
        if not self.current_file:
            self.save_file_as()
            return
        
        try:
            content = self.editor.get("1.0", tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.file_modified = False
            self.update_title()
            self.status_bar.config(text=f"Saved: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def save_file_as(self):
        """Save file as"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".abu",
            filetypes=[("AbuLang files", "*.abu"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.current_file = filename
            self.save_file()

    def update_title(self):
        """Update window title"""
        title = "AbuLang IDLE"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.file_modified:
            title += " *"
        self.root.title(title)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "AbuLang IDLE v3.0.0\n\nA friendly programming language with IDLE shell")

    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def main():
    """Entry point for IDLE GUI"""
    root = tk.Tk()
    idle = AbuIDLEGUI(root)
    idle.run()


if __name__ == "__main__":
    main()
