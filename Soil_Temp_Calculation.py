import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Function to compute soil temperature for each row
def compute_soil_temperature():
    try:
        # Get values from input fields
        file_path = file_path_var.get()
        z_cm = float(entry_depth.get())       # Soil depth in cm
        alpha = float(entry_alpha.get())      # Thermal diffusivity (m²/s)

        # Basic input validation
        if not file_path:
            messagebox.showerror("Input Error", "Please select an input CSV file.")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("File Error", "Selected input file does not exist.")
            return

        # Read the input CSV file, skipping the second row (index 1)
        # because it might contain units or headers you want to ignore.
        df = pd.read_csv(file_path, skiprows=[1])

        # Ensure required columns exist
        for col in ["Date", "T.Max", "T.Min"]:
            if col not in df.columns:
                messagebox.showerror("Format Error", f"Missing column: {col}. Please check your CSV file header.")
                return

        # Convert soil depth from cm to meters
        z = z_cm / 100
        p = 86400  # Period = 1 day in seconds

        # Use the year from the first row's date as the start date
        # Note: After skiprows=[1], the first row of actual data is now df.iloc[0]
        first_date = str(df.iloc[0]["Date"])
        year = int(first_date[:4]) # Assuming date format YYYYMMDD, so first 4 chars are year
        start_date = datetime(year, 1, 1)

        # Function to calculate soil temperature for one row
        def calc_temp(row):
            try:
                # Convert date to datetime object
                # Assuming 'Date' column is in YYYYMMDD integer format, e.g., 20240101
                date_obj = datetime.strptime(str(int(row["Date"])), "%Y%m%d")
                t_days = (date_obj - start_date).days # Days since start of the year
                t_sec = t_days * 86400 # Convert days to seconds

                # Get Tmax and Tmin
                Tmax = float(row["T.Max"])
                Tmin = float(row["T.Min"])
                Tm = (Tmax + Tmin) / 2 # Mean daily temperature
                Aa = (Tmax - Tmin) / 2 # Amplitude of daily temperature variation

                # Compute soil temperature using the formula
                # Decay factor: exp(-z * sqrt(pi / (alpha * P)))
                decay = np.exp(-z * np.sqrt(np.pi / (alpha * p)))
                # Phase shift: (2 * pi * t_sec / P) - z * sqrt(pi / (alpha * P))
                phase_shift = (2 * np.pi * t_sec / p) - z * np.sqrt(np.pi / (alpha * p))
                
                T = Tm + Aa * decay * np.sin(phase_shift)
                return round(T, 2)
            except ValueError:
                # Handle cases where T.Max, T.Min, or Date cannot be converted to float/int
                # print(f"Skipping row due to invalid data in T.Max/T.Min/Date: {row.to_dict()}") # Optional: for debugging
                return np.nan # Return NaN (Not a Number) for rows with errors
            except Exception as e:
                # Catch any other unexpected errors during calculation for a row
                # print(f"An unexpected error occurred in calc_temp: {e} for row: {row.to_dict()}") # Optional: for debugging
                return np.nan

        # Apply the function to every row to compute Soil_Temperature
        df["Soil_Temperature"] = df.apply(calc_temp, axis=1)

        # --- New feature: Save file dialog ---
        # Suggest a default filename based on the input file's name
        # e.g., if input is "data.csv", suggestion will be "data_with_soil_temp.csv"
        suggested_filename = os.path.splitext(os.path.basename(file_path))[0] + "_with_soil_temp.csv"

        # Open a "Save As" dialog for the user to choose save location and filename
        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv", # Automatically add .csv if user doesn't type it
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], # Filter file types
            initialfile=suggested_filename, # Pre-fill with the suggested filename
            title="Save Soil Temperature Results" # Dialog box title
        )

        # If user cancels the save dialog, output_path will be an empty string
        if not output_path:
            messagebox.showinfo("Cancelled", "File save operation was cancelled by the user.")
            return

        # Save the DataFrame to the selected path
        df.to_csv(output_path, index=False) # index=False prevents writing DataFrame index as a column

        messagebox.showinfo("Success", f"Output saved to:\n{output_path}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please ensure 'Soil Depth' and 'Alpha' are valid numbers. Also check your CSV file for correct data format (Date, T.Max, T.Min).")
    except FileNotFoundError:
        messagebox.showerror("File Error", "The selected file was not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Create main Tkinter window
root = tk.Tk()
root.title("Soil Temperature Calculator") # Set window title

# Set initial window size
root.geometry("650x320") # Width x Height in pixels

# Configure grid to allow widgets to expand and maintain proportions
# Column 0: for labels (e.g., "Select Input CSV file:") - fixed width
root.grid_columnconfigure(0, weight=0)
# Column 1: for Entry widgets (input fields) - expands more
root.grid_columnconfigure(1, weight=3)
# Column 2: for buttons (e.g., "Load File") - fixed width
root.grid_columnconfigure(2, weight=0)

# Configure rows to allow vertical expansion, distributing space evenly
for i in range(4): # For rows 0, 1, 2, 3 (containing main elements)
    root.grid_rowconfigure(i, weight=1)


# === File selection (Input CSV) UI ===
file_path_var = tk.StringVar()

def browse_input_file():
    path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Select Input CSV File"
    )
    if path:
        file_path_var.set(path)

tk.Label(root, text="Select Input CSV file:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
# Entry widget for file path, sticky "ew" makes it expand horizontally
tk.Entry(root, textvariable=file_path_var).grid(row=0, column=1, padx=10, pady=5, sticky="ew")
# "Load File" button
tk.Button(root, text="Load File", command=browse_input_file).grid(row=0, column=2, padx=5, pady=5, sticky="w")


# === Soil Depth input UI ===
tk.Label(root, text="Soil Depth (cm):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_depth = tk.Entry(root)
entry_depth.insert(0, "10") # Default depth value, e.g., 10 cm
entry_depth.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

# === Thermal Diffusivity (Alpha) input UI ===
tk.Label(root, text="Alpha (m²/s):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_alpha = tk.Entry(root)
entry_alpha.insert(0, "5e-7")  # Default alpha value = 5×10^-7. User can edit this.
entry_alpha.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

# === Calculate and Save Button ===
# This button spans across all 3 columns and expands in all directions
tk.Button(
    root,
    text="Calculate & Save Soil Temperature", # Button text
    command=compute_soil_temperature,
    bg="#4CAF50", # Background color (green)
    fg="white",   # Foreground color (text color)
    font=("Helvetica", 10, "bold"), # Font style
    height=2 # Height of the button in text units
).grid(row=3, column=0, columnspan=3, pady=15, sticky="nsew") # columnspan makes it span all columns, sticky makes it fill

# Start the Tkinter event loop
root.mainloop()