"""Main entry point for the package."""

import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bowens Island Private Parties connector"
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="Run in command-line mode"
    )
    parser.add_argument(
        "--gui", action="store_true",
        help="Run in graphical mode (default)"
    )
    parser.add_argument(
        "--command", type=str,
        help="Command to execute in CLI mode"
    )
    
    args, remaining_args = parser.parse_known_args()
    
    # Default to GUI mode
    if not args.cli and not args.gui:
        args.gui = True
    
    if args.cli:
        # Run in CLI mode
        from src.cli import main as cli_main
        sys.argv = [sys.argv[0]] + (
            [args.command] if args.command else []
        ) + remaining_args
        cli_main()
    else:
        # Run in GUI mode
        try:
            import tkinter
            from src.gui import main as gui_main
            gui_main()
        except ImportError:
            print("Error: Tkinter is not available. Run with --cli for command-line mode.")
            sys.exit(1)

if __name__ == "__main__":
    main()
