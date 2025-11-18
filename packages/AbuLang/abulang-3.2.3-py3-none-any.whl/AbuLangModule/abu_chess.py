"""
AbuChess - Chess AI Package
"""

def info():
    """Show AbuChess information"""
    print("""
=== AbuChess - Neural Chess AI ===

Features:
  - Neural network chess engine
  - Multiple difficulty levels
  - Web interface
  - CLI interface
  - Training with Stockfish

Usage:
  chess.AIweb()    - Launch web interface (recommended!)
  chess.play()     - Launch CLI game
  chess.train()    - Train the AI
  chess.status()   - Check installation

Note: AbuChess requires additional dependencies.
Install with: pip install abulang[chess]
""")

def status():
    """Check AbuChess installation status"""
    print("Checking AbuChess dependencies...")
    
    deps = {
        "python-chess": "Chess library",
        "torch": "Neural network (PyTorch)",
        "flask": "Web server",
        "flask-cors": "Web CORS support"
    }
    
    all_installed = True
    for package, desc in deps.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package:15} - {desc}")
        except ImportError:
            print(f"  ✗ {package:15} - {desc} (NOT INSTALLED)")
            all_installed = False
    
    if all_installed:
        print("\n✓ AbuChess is ready!")
    else:
        print("\n✗ Install missing dependencies:")
        print("  pip install abulang[chess]")

def AIweb():
    """Launch AbuChess web interface"""
    try:
        import sys
        import os
        
        # Try to import the web interface
        chess_path = os.path.join(os.path.dirname(__file__), "..", "06.AI")
        if os.path.exists(chess_path):
            sys.path.insert(0, chess_path)
            from web_interface import start_server
            start_server()
        else:
            print("AbuChess web interface not found")
            print("Make sure 06.AI folder is in the project")
    except ImportError as e:
        print(f"Could not start web interface: {e}")
        print("Install dependencies: pip install abulang[chess]")

def play():
    """Launch AbuChess CLI game"""
    try:
        import sys
        import os
        
        chess_path = os.path.join(os.path.dirname(__file__), "..", "06.AI")
        if os.path.exists(chess_path):
            sys.path.insert(0, chess_path)
            from cli_game import start_game
            start_game()
        else:
            print("AbuChess CLI not found")
            print("Make sure 06.AI folder is in the project")
    except ImportError as e:
        print(f"Could not start CLI game: {e}")
        print("Install dependencies: pip install abulang[chess]")

def train():
    """Launch AbuChess training"""
    try:
        import sys
        import os
        
        chess_path = os.path.join(os.path.dirname(__file__), "..", "06.AI")
        if os.path.exists(chess_path):
            sys.path.insert(0, chess_path)
            from training import start_training
            start_training()
        else:
            print("AbuChess training not found")
            print("Make sure 06.AI folder is in the project")
    except ImportError as e:
        print(f"Could not start training: {e}")
        print("Install dependencies: pip install abulang[chess]")
