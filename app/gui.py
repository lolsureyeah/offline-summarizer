# app/gui.py
"""
Defines the main application GUI window, widgets, and event handlers.
"""
import tkinter
import customtkinter as ctk
from tkinter import filedialog
import threading
import pyperclip
from .logic import process_document, get_ollama_models
from .ocr import is_tesseract_available

class App(ctk.CTk):
    """Main application class inheriting from customtkinter.CTk."""
    def __init__(self):
        super().__init__()
        self.title("Offline Document Summarizer & Assistant")
        self.geometry("900x800")
        self.selected_file_path = ""
        self.ollama_models = ["No Models Found"]

        self._create_widgets()
        self.check_ocr_status()
        self.populate_model_list()

    def _create_widgets(self):
        """Creates and packs all the GUI widgets."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- Top Row: File & Model Selection ---
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(pady=10, padx=10, fill="x")
        top_frame.grid_columnconfigure(1, weight=1)

        self.file_button = ctk.CTkButton(top_frame, text="Select Document", command=self.select_file)
        self.file_button.grid(row=0, column=0, padx=(0, 10))

        self.file_label = ctk.CTkLabel(top_frame, text="No file selected", anchor="w")
        self.file_label.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(top_frame, text="Select Model:").grid(row=0, column=2, padx=(20, 10))
        self.model_menu = ctk.CTkOptionMenu(top_frame, values=self.ollama_models)
        self.model_menu.grid(row=0, column=3)

        # --- Unified Input Options Frame ---
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(pady=10, padx=10, fill="x")
        options_frame.grid_columnconfigure(1, weight=1)

        # Summarize Options
        ctk.CTkLabel(options_frame, text="Summary Length (%):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.length_entry = ctk.CTkEntry(options_frame, placeholder_text="e.g., 20", width=120)
        self.length_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(options_frame, text="Focus Keywords (optional):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.keywords_entry = ctk.CTkEntry(options_frame, placeholder_text="e.g., python, machine learning")
        self.keywords_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Q&A Option - Visually Separated
        question_frame = ctk.CTkFrame(main_frame)
        question_frame.pack(pady=15, padx=10, fill="x")
        question_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(question_frame, text="Or, Ask a Question about the Document:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.question_entry = ctk.CTkEntry(question_frame, placeholder_text="e.g., What was the main conclusion?")
        self.question_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # --- Action Button ---
        self.action_button = ctk.CTkButton(main_frame, text="Generate", command=self.start_task_thread, state="disabled")
        self.action_button.pack(pady=20, padx=10)

        self.status_label = ctk.CTkLabel(main_frame, text="Welcome! Please select a document.", text_color="gray")
        self.status_label.pack(pady=5, padx=10)

        # --- Output Area ---
        output_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        output_frame.pack(pady=10, padx=10, fill="both", expand=True)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

        self.summary_textbox = ctk.CTkTextbox(output_frame, wrap="word", state="disabled", fg_color="transparent", border_width=2)
        self.summary_textbox.grid(row=0, column=0, sticky="nsew")

        output_button_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_button_frame.grid(row=1, column=0, sticky="ew", pady=(10,0))
        output_button_frame.grid_columnconfigure(0, weight=1)

        self.copy_button = ctk.CTkButton(output_button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, state="disabled")
        self.copy_button.pack(side="right", padx=(10,0))
        self.save_button = ctk.CTkButton(output_button_frame, text="Save to File", command=self.save_to_file, state="disabled")
        self.save_button.pack(side="right")

    def populate_model_list(self):
        """Fetches installed Ollama models and populates the dropdown."""
        try:
            self.ollama_models = get_ollama_models()
            if not self.ollama_models:
                self.ollama_models = ["No Models Found"]
            self.model_menu.configure(values=self.ollama_models)
        except Exception as e:
            self.status_label.configure(text=f"Error fetching models: {e}", text_color="lightcoral")

    def select_file(self):
        """Opens a file dialog and enables the action button."""
        self.selected_file_path = filedialog.askopenfilename(title="Select a Document", filetypes=[("Documents", "*.txt *.docx *.pdf")])
        if self.selected_file_path:
            filename = self.selected_file_path.split('/')[-1]
            self.file_label.configure(text=filename)
            self.action_button.configure(state="normal")
            self.status_label.configure(text="File selected. Ready to generate.", text_color="gray")

    def start_task_thread(self):
        """Starts the backend processing in a separate thread."""
        if not self.selected_file_path: return

        selected_model = self.model_menu.get()
        if selected_model == "No Models Found":
            self.status_label.configure(text="Error: No Ollama models found. Please install a model first.", text_color="lightcoral")
            return
            
        self.action_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.status_label.configure(text="Processing...", text_color="white")
        
        self.summary_textbox.configure(state="normal")
        self.summary_textbox.delete("1.0", "end")
        
        params = {
            "model": selected_model, "file_path": self.selected_file_path,
            "length_str": self.length_entry.get(), "keywords_str": self.keywords_entry.get(),
            "question_str": self.question_entry.get(), "update_status": lambda msg: self.status_label.configure(text=msg)
        }
        
        thread = threading.Thread(target=self.run_task_logic, args=(params,))
        thread.daemon = True
        thread.start()

    def run_task_logic(self, params):
        """The core logic that runs in the thread, processing the document and updating the GUI."""
        try:
            final_output = process_document(params)
            self.summary_textbox.insert("1.0", final_output)
            self.status_label.configure(text="Generated successfully!", text_color="lightgreen")
            self.copy_button.configure(state="normal")
            self.save_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="lightcoral")
        finally:
            self.summary_textbox.configure(state="disabled")
            self.action_button.configure(state="normal")

    def copy_to_clipboard(self):
        """Copies the content of the summary textbox to the clipboard."""
        try:
            pyperclip.copy(self.summary_textbox.get("1.0", "end-1c"))
            self.status_label.configure(text="Copied to clipboard!", text_color="white")
        except Exception as e:
            self.status_label.configure(text=f"Copy failed: {e}", text_color="lightcoral")

    def save_to_file(self):
        """Saves the content of the summary textbox to a text file."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save As..."
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.summary_textbox.get("1.0", "end-1c"))
                self.status_label.configure(text=f"Saved to {file_path.split('/')[-1]}", text_color="white")
        except Exception as e:
            self.status_label.configure(text=f"Save failed: {e}", text_color="lightcoral")
            
    def check_ocr_status(self):
        """Checks if Tesseract is installed and displays status at the bottom."""
        status = "OCR Engine (Tesseract): Found" if is_tesseract_available() else "OCR Engine (Tesseract): Not Found. Install for full PDF support."
        ctk.CTkLabel(self, text=status, text_color="gray").pack(side="bottom", pady=5)