"""
AbuChess - Neural Chess AI integration for AbuLang
Integrates the Abu Chess AI from 06.AI directory
"""

import os
import sys
import subprocess
import webbrowser
import time

class AbuChess:
    """Chess AI integration for AbuLang"""
    
    def __init__(self):
        self.chess_dir = "06.AI"
        self.web_server_running = False
        self._check_installation()
    
    def _check_installation(self):
        """Check if 06.AI directory exists"""
        if not os.path.exists(self.chess_dir):
            print("[AbuChess] Warning: 06.AI directory not found")
            print("[AbuChess] Some features may not be available")
    
    def play(self):
        """
        Launch the chess game CLI
        Usage: from AbuChess import play
        """
        if not os.path.exists(self.chess_dir):
            print("[AbuChess Error] 06.AI directory not found")
            print("[AbuChess] Please ensure the chess AI is installed")
            return False
        
        main_path = os.path.join(self.chess_dir, "main.py")
        
        if not os.path.exists(main_path):
            print("[AbuChess Error] main.py not found in 06.AI")
            return False
        
        try:
            print("[AbuChess] Launching Abu Chess AI...")
            print("[AbuChess] Starting game interface...")
            
            # Get absolute path to chess directory
            abs_chess_dir = os.path.abspath(self.chess_dir)
            
            # Run main.py from the chess directory
            subprocess.run([sys.executable, "main.py"], cwd=abs_chess_dir)
            
            return True
        except Exception as e:
            print(f"[AbuChess Error] Could not launch game: {e}")
            return False
    
    def AIweb(self):
        """
        Launch the web interface
        Opens localhost and starts web_server.py
        Usage: from AbuChess import AIweb
        """
        if not os.path.exists(self.chess_dir):
            print("[AbuChess Error] 06.AI directory not found")
            return False
        
        web_server_path = os.path.join(self.chess_dir, "web_server.py")
        
        if not os.path.exists(web_server_path):
            print("[AbuChess Error] web_server.py not found in 06.AI")
            return False
        
        try:
            print("[AbuChess] Starting Abu Chess AI Web Server...")
            print("[AbuChess] Server will start at http://localhost:5000")
            print("[AbuChess] Opening browser...")
            
            # Get absolute path to chess directory
            abs_chess_dir = os.path.abspath(self.chess_dir)
            
            # Start web server in background
            process = subprocess.Popen(
                [sys.executable, "web_server.py"],
                cwd=abs_chess_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Open browser
            webbrowser.open("http://localhost:5000")
            
            print("[AbuChess] ✓ Web server started!")
            print("[AbuChess] Browser opened to http://localhost:5000")
            print("[AbuChess] Press Ctrl+C in terminal to stop server")
            
            # Keep process running
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n[AbuChess] Stopping web server...")
                process.terminate()
                print("[AbuChess] Server stopped")
            
            return True
            
        except Exception as e:
            print(f"[AbuChess Error] Could not start web server: {e}")
            return False
    
    def train(self):
        """
        Launch training interface
        """
        if not os.path.exists(self.chess_dir):
            print("[AbuChess Error] 06.AI directory not found")
            return False
        
        print("[AbuChess] To train Abu:")
        print("[AbuChess] 1. Run: chess.play()")
        print("[AbuChess] 2. Select option 4 (Train Model)")
        print("[AbuChess] 3. Follow the training wizard")
        
        return self.play()
    
    def info(self):
        """Display information about Abu Chess AI"""
        print("\n" + "="*60)
        print("  ABU CHESS AI - Neural Network Chess Engine")
        print("="*60)
        print("\nFeatures:")
        print("  • Neural network-based chess AI")
        print("  • Multiple difficulty levels (Beginner, Intermediate, Advanced)")
        print("  • Training with Stockfish")
        print("  • Web interface with beautiful UI")
        print("  • Move analysis and evaluation")
        print("  • Command-line interface")
        
        print("\nUsage:")
        print("  chess.play()    - Launch CLI game")
        print("  chess.AIweb()   - Launch web interface")
        print("  chess.train()   - Train the AI")
        print("  chess.info()    - Show this information")
        
        print("\nQuick Start:")
        print("  1. Play in browser:  chess.AIweb()")
        print("  2. Play in terminal: chess.play()")
        print("  3. Train Abu:        chess.train()")
        
        print("\nImport Options:")
        print("  libra AbuChess              # Import module")
        print("  from AbuChess import play   # Direct play function")
        print("  from AbuChess import AIweb  # Direct web function")
        
        if os.path.exists(self.chess_dir):
            print(f"\n✓ Chess AI found at: {self.chess_dir}")
        else:
            print(f"\n✗ Chess AI not found at: {self.chess_dir}")
        
        print("="*60 + "\n")
    
    def status(self):
        """Check installation status"""
        print("\n[AbuChess] Installation Status:")
        
        # Check directory
        if os.path.exists(self.chess_dir):
            print(f"  ✓ Chess AI directory found: {self.chess_dir}")
        else:
            print(f"  ✗ Chess AI directory not found: {self.chess_dir}")
            return
        
        # Check main files
        files_to_check = [
            "main.py",
            "web_server.py",
            "requirements.txt",
            "README.md"
        ]
        
        for file in files_to_check:
            path = os.path.join(self.chess_dir, file)
            if os.path.exists(path):
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} (missing)")
        
        # Check abu package
        abu_dir = os.path.join(self.chess_dir, "abu")
        if os.path.exists(abu_dir):
            print(f"  ✓ abu package")
        else:
            print(f"  ✗ abu package (missing)")
        
        # Check models
        models_dir = os.path.join(self.chess_dir, "models")
        if os.path.exists(models_dir):
            models = [f for f in os.listdir(models_dir) if f.endswith('.pth')]
            if models:
                print(f"  ✓ Trained models found: {len(models)}")
            else:
                print(f"  ⚠ No trained models (train Abu to create one)")
        else:
            print(f"  ⚠ Models directory not found")
        
        print("\n[AbuChess] Ready to play!")
    
    # Convenience methods
    def new_game(self):
        """Start a new game (alias for play)"""
        return self.play()
    
    def web(self):
        """Launch web interface (alias for AIweb)"""
        return self.AIweb()


# Create singleton instance
chess = AbuChess()

# Export functions for direct import
def play():
    """Launch chess game CLI"""
    return chess.play()

def AIweb():
    """Launch web interface"""
    return chess.AIweb()

def train():
    """Launch training interface"""
    return chess.train()

def info():
    """Show information"""
    return chess.info()

def status():
    """Check installation status"""
    return chess.status()
