# ./src/pytermtalk_ref/__init__.py
"""
A Python reference implementation of a terminal-based chat program using sockets.
Supports both server and client modes. This project serves as a starting point
for building a production-ready terminal chat application.

Warning: This script does **not** provide authentication. 
         Do **not** use it for production or sensitive purposes.

Original script by Andrea Ciarrocchi was published in Linux Magazine, October 2025.
"""

from .chat import main as chat_main


# -----------------------------------------------------------------------------
#   Funcion main()
# -----------------------------------------------------------------------------


def main() -> None:
    """Entry point package."""
    chat_main()

# === END ===
