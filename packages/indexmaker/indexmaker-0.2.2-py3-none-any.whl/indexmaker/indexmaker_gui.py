import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
from indexmaker.indexmaker_script import IndexMaker
import threading


class IndexMakerGUI():

    def __init__(self):


        # Create the GUI
        self.root = tk.Tk()
        self.root.title("IndexMaker GUI")

        #intro label
        self.explanations = """
        IndexMaker
        ----------------------
        (c) Nicolas Soler 2025
        Enter a pdf file path, an optional index file path, 
        output file path, and starting page number.

        The script will generate an index of all
        non-common words found in the PDF (in docx format).
        """
        self.intro_label = tk.Label(self.root, text=self.explanations, font=("Helvetica", 12), bg="lightyellow", justify=tk.LEFT)
        self.intro_label.pack(pady=10)

        # PDF file selection
        self.pdf_label = tk.Label(self.root, text="Select PDF File:")
        self.pdf_label.pack(pady=5)
        self.pdf_entry = tk.Entry(self.root, width=50)
        self.pdf_entry.pack(pady=5)
        self.pdf_button = tk.Button(self.root, text="Browse", command=self.select_pdf)
        self.pdf_button.pack(pady=5)

        # Optional index file selection
        self.index_label = tk.Label(self.root, text="Optional Index File:")
        self.index_label.pack(pady=5)
        self.index_entry = tk.Entry(self.root, width=50)
        self.index_entry.pack(pady=5)
        self.index_button = tk.Button(self.root, text="Browse", command=self.select_index_file)
        self.index_button.pack(pady=5)

        # Output file path
        self.output_label = tk.Label(self.root, text="Output File Path:")
        self.output_label.pack(pady=5)
        self.output_entry = tk.Entry(self.root, width=50)
        self.output_entry.insert(0, "output_index.docx")  # Default output file name
        self.output_entry.pack(pady=5)

        # Start page input
        self.start_page_label = tk.Label(self.root, text="Page number of the document you consider as the first page:")
        self.start_page_label.pack(pady=5)
        self.start_page_entry = tk.Entry(self.root, width=50)
        self.start_page_entry.insert(0, "1")  # Default start page
        self.start_page_entry.pack(pady=5)

        # Run button
        self.run_button = tk.Button(self.root, text="Run!", bg="blue", fg="white", command=self.run_script)
        self.run_button.pack(pady=10)

        # Output area
        self.output_label = tk.Label(self.root, text="Script Output:")
        self.output_label.pack(pady=5)

        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=10)
        self.output_area.pack(pady=5)

        # Output file button
        self.output_button = tk.Button(self.root, text="Open Output File", command=self.open_output, state=tk.DISABLED)
        self.output_button.pack(pady=5)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", bg="red3", fg="white", command=self.root.quit)
        self.quit_button.pack(pady=5)

        # index_maker object
        self.index_maker = None


    def init_index_maker(self):
        pdf_file = self.pdf_entry.get()
        index_file = self.index_entry.get()
        output_file = self.output_entry.get()
        start_page = self.start_page_entry.get()

        if not pdf_file:
            messagebox.showerror("Error", "Please select a PDF file.")
            return

        self.index_maker = IndexMaker(
                input_file_path=pdf_file,
                output_docx=output_file,
                start_from_page=start_page,
                own_index=index_file if index_file.strip() else None,
                gui_obj=self,
            )

    def display_msg(self, msg:str, clearscreen:bool=False):
        if clearscreen:
            self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, msg+"\n")

    # Function to select a PDF file
    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")],
            title="Select a PDF File"
        )
        if file_path:
            self.pdf_entry.delete(0, tk.END)
            self.pdf_entry.insert(0, file_path)

    # Function to select an optional index file
    def select_index_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")],
            title="Select an Index File"
        )
        if file_path:
            self.index_entry.delete(0, tk.END)
            self.index_entry.insert(0, file_path)

    def run_script(self):
        """
        Function to run the index maker script
        """
        # Display processing message
        self.display_msg("\nProcessing, please wait...")

        def task():
            try:
                # Create the index_maker
                self.init_index_maker()

                # Run it
                output_file = self.index_maker.main()
                self.display_msg(f"Index created successfully: {output_file}")

                # Enable the "Open Output File" button
                if os.path.exists(output_file):
                    self.output_button.config(state=tk.NORMAL, bg="lightgreen")
                else:
                    self.output_button.config(state=tk.DISABLED)

            except Exception as e:
                self.display_msg(f"An error occurred: {str(e)}")

        # Run the task in a separate thread from the one running the GUI
        threading.Thread(target=task).start()

    # Function to open the output file
    def open_output(self):
        output_file = self.output_entry.get()
        if os.path.exists(output_file):
            # open it for linux, mac windows
            os.startfile(output_file) if os.name == "nt" else os.system(f"xdg-open {output_file}")
        else:
            messagebox.showerror("Error", "Output file cannot be opened or not found.")


    def run(self):
        # Start the GUI event loop
        self.root.mainloop()

def main():
    gui = IndexMakerGUI()
    gui.run()

if __name__ == "__main__":
    main()
