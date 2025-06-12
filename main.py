# main.py
"""
Main entry point for the Offline Document Summarizer application.
Initializes and runs the graphical user interface.
"""
from app.gui import App

if __name__ == "__main__":
    app = App()
    app.mainloop()