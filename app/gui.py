# app/gui.py
"""
Defines the main application GUI window, widgets, and event handlers.
"""
import tkinter
import customtkinter as ctk
from tkinter import filedialog
import threading
from .logic import generate_summary
from .ocr import is_tesseract_available

class App(ctk.CTk):
    """Main application class inheriting from customtkinter.CTk."""
    def __init__(self):
        super().__init__()
        self.title("Offline Document Summarizer")
        self.geometry("800x600")
        self.selected_file_path = ""

        # --- Widget Creation ---
        self._create_widgets()
        
        # --- Check for OCR on startup ---
        self.check_ocr_status()

    def _create_widgets(self):
        """Creates and packs all the GUI widgets."""
        self.file_button = ctk.CTkButton(self, text="Select Document", command=self.select_file)
        self.file_button.pack(pady=10, padx=20)

        self.file_label = ctk.CTkLabel(self, text="No file selected")
        self.file_label.pack(pady=5, padx=20)
        
        self.summarize_button = ctk.CTkButton(self, text="Generate Summary", command=self.start_summary_thread, state="disabled")
        self.summarize_button.pack(pady=10, padx=20)

        self.status_label = ctk.CTkLabel(self, text="Welcome! Please select a document.", text_color="gray")
        self.status_label.pack(pady=5, padx=20)
        
        self.summary_textbox = ctk.CTkTextbox(self, wrap="word", state="disabled", fg_color="transparent")
        self.summary_textbox.pack(pady=10, padx=10, fill="both", expand=True)

    def check_ocr_status(self):
        """Checks if Tesseract is installed and updates a label at the bottom."""
        status = "OCR Engine (Tesseract): Found" if is_tesseract_available() else "OCR Engine (Tesseract): Not Found. Install for full PDF support."
        ctk.CTkLabel(self, text=status, text_color="gray").pack(side="bottom", pady=5)

    def select_file(self):
        """Opens a file dialog to select a document and enables the summarize button."""
        self.selected_file_path = filedialog.askopenfilename(
            title="Select a Document",
            filetypes=[("Documents", "*.txt *.docx *.pdf")]
        )
        if self.selected_file_path:
            # Display only the filename, not the full path
            filename = self.selected_file_path.split('/')[-1]
            self.file_label.configure(text=filename)
            self.summarize_button.configure(state="normal")
            self.status_label.configure(text="File selected. Ready to summarize.", text_color="gray")

    def start_summary_thread(self):
        """Starts the summarization process in a separate thread to keep the GUI responsive."""
        if not self.selected_file_path:
            return
        self.summarize_button.configure(state="disabled")
        self.status_label.configure(text="Processing...", text_color="white")
        
        # Clear previous summary
        self.summary_textbox.configure(state="normal")
        self.summary_textbox.delete("1.0", "end")
        self.summary_textbox.configure(state="disabled")
        
        thread = threading.Thread(target=self.run_summary_logic)
        thread.daemon = True  # Allows main window to close even if thread is running
        thread.start()

    def run_summary_logic(self):
        """The core logic that runs in a separate thread. Calls the backend and updates the GUI."""
        try:
            final_summary = generate_summary(
                file_path=self.selected_file_path,
                update_status=lambda msg: self.status_label.configure(text=msg)
            )
            
            # Update GUI components safely from the thread
            self.summary_textbox.configure(state="normal")
            self.summary_textbox.insert("1.0", final_summary)
            self.summary_textbox.configure(state="disabled")
            self.status_label.configure(text="Summary generated successfully!", text_color="lightgreen")

        except Exception as e:
            # Display any errors from the backend directly in the GUI
            self.status_label.configure(text=f"Error: {e}", text_color="lightcoral")
        finally:
            # Re-enable the button regardless of success or failure
            self.summarize_button.configure(state="normal")