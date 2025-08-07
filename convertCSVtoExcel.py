import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to convert CSVs to Excel
def convert_csvs_to_excel():
    # Ask user to select multiple CSV files
    file_paths = filedialog.askopenfilenames(
        title="Select CSV files",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not file_paths:
        messagebox.showinfo("No File Selected", "No CSV files were selected.")
        return

    for file_path in file_paths:
        try:
            # Read CSV
            df = pd.read_csv(file_path)

            # Construct Excel file path
            excel_path = os.path.splitext(file_path)[0] + ".xlsx"

            # Save to Excel
            df.to_excel(excel_path, index=False)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {file_path}:\n{str(e)}")
            return

    messagebox.showinfo("Success", "All CSV files have been converted to Excel.")

# Set up GUI
root = tk.Tk()
root.withdraw()  # Hide the main window

# Run the converter
convert_csvs_to_excel()
