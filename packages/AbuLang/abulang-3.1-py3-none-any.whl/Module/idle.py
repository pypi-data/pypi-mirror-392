"""
AbuLang IDLE - Interactive shell like Python IDLE
"""

import sys
from .runner import AbuRunner


class AbuIDLE:
    """Interactive AbuLang shell"""

    def __init__(self):
        self.runner = AbuRunner()
        self.history = []
        self.running = True

    def start(self):
        """Start the IDLE shell"""
        self.print_banner()
        self.repl_loop()

    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*60)
        print("  AbuLang IDLE v3.0.0")
        print("  Interactive Shell")
        print("="*60)
        print("\nType 'help' for help, 'exit' to quit\n")

    def repl_loop(self):
        """Main REPL loop"""
        while self.running:
            try:
                # Get user input
                prompt = ">>> "
                user_input = input(prompt).strip()

                # Handle empty input
                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() == "exit":
                    self.print_goodbye()
                    break

                if user_input.lower() == "history":
                    self.show_history()
                    continue

                if user_input.lower() == "clear":
                    self.clear_screen()
                    continue

                # Add to history
                self.history.append(user_input)

                # Execute command
                self.runner.execute_line(user_input)

            except KeyboardInterrupt:
                print("\n\n[Interrupted]")
                continue
            except EOFError:
                print("\n")
                self.print_goodbye()
                break
            except Exception as e:
                print(f"[Error] {e}")

    def show_history(self):
        """Show command history"""
        print("\n--- Command History ---")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i:3}. {cmd}")
        print()

    def clear_screen(self):
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

    def print_goodbye(self):
        """Print goodbye message"""
        print("\n" + "="*60)
        print("  Thanks for using AbuLang!")
        print("="*60 + "\n")


def main():
    """Entry point for IDLE"""
    idle = AbuIDLE()
    idle.start()


if __name__ == "__main__":
    main()
