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
        self.geometry("800x750") # Increased height for new fields
        self.selected_file_path = ""

        self._create_widgets()
        self.check_ocr_status()

    def _create_widgets(self):
        """Creates and packs all the GUI widgets."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- File Selection ---
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(pady=10, padx=10, fill="x")

        self.file_button = ctk.CTkButton(top_frame, text="Select Document", command=self.select_file)
        self.file_button.pack(side="left", padx=(0, 10))

        self.file_label = ctk.CTkLabel(top_frame, text="No file selected", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)

        # --- New Feature Inputs ---
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(options_frame, text="Summary Length (% of original):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.length_entry = ctk.CTkEntry(options_frame, placeholder_text="e.g., 20", width=120)
        self.length_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(options_frame, text="Focus Keywords (comma-separated):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.keywords_entry = ctk.CTkEntry(options_frame, placeholder_text="e.g., python, machine learning")
        self.keywords_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        options_frame.grid_columnconfigure(1, weight=1) # Allow keywords entry to expand

        self.summarize_button = ctk.CTkButton(main_frame, text="Generate Summary", command=self.start_summary_thread, state="disabled")
        self.summarize_button.pack(pady=20, padx=10)

        self.status_label = ctk.CTkLabel(main_frame, text="Welcome! Please select a document.", text_color="gray")
        self.status_label.pack(pady=5, padx=10)
        
        self.summary_textbox = ctk.CTkTextbox(main_frame, wrap="word", state="disabled", fg_color="transparent", border_width=2)
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
        
        self.summary_textbox.configure(state="normal")
        self.summary_textbox.delete("1.0", "end")
        self.summary_textbox.configure(state="disabled")
        
        # Get values from new entry fields
        length_str = self.length_entry.get()
        keywords_str = self.keywords_entry.get()
        
        thread = threading.Thread(target=self.run_summary_logic, args=(length_str, keywords_str))
        thread.daemon = True
        thread.start()

    def run_summary_logic(self, length_str, keywords_str):
        """The core logic that runs in a separate thread. Calls the backend and updates the GUI."""
        try:
            final_summary = generate_summary(
                file_path=self.selected_file_path,
                length_percentage_str=length_str,
                keywords_str=keywords_str,
                update_status=lambda msg: self.status_label.configure(text=msg)
            )
            
            self.summary_textbox.configure(state="normal")
            self.summary_textbox.insert("1.0", final_summary)
            self.summary_textbox.configure(state="disabled")
            self.status_label.configure(text="Summary generated successfully!", text_color="lightgreen")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="lightcoral")
        finally:
            self.summarize_button.configure(state="normal")