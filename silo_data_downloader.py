import csv
import tkinter as tk
from tkinter import messagebox

import requests


def load_stations(filepath):
    station_dict = {}
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            keys = list(reader.fieldnames)
            for row in reader:
                station_num = row.get(keys[0], "").strip()
                station_name = row.get(keys[1], "").strip()
                lat = row.get(keys[2], "").strip()
                lon = row.get(keys[3], "").strip()
                if station_num and station_name and lat and lon:
                    station_dict[station_name] = {
                        "number": station_num,
                        "lat": lat,
                        "lon": lon,
                    }
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load station list: {e}")
    return station_dict


def build_silo_url_grid(lat, lon, start_date, end_date, email):
    email_encoded = email.replace("@", "%40")
    return (
        f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/DataDrillDataset.php"
        f"?format=alldata&lat={lat}&lon={lon}"
        f"&start={start_date}&finish={end_date}"
        f"&username={email_encoded}&password=apirequest&comment=csv"
    )


def build_silo_url_station(station_num, start_date, end_date, email):
    email_encoded = email.replace("@", "%40")
    return (
        f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/PatchedPointDataset.php"
        f"?format=alldata&station={station_num}"
        f"&start={start_date}&finish={end_date}"
        f"&username={email_encoded}&password=apirequest&comment=csv"
    )


def update_station_list(event=None):
    search_term = entry_search.get().strip().lower()
    station_listbox.delete(0, "end")
    for name in stations:
        if search_term in name.lower():
            station_listbox.insert("end", name)


def download_data():
    mode = var_mode.get()
    start = entry_start.get().strip()
    end = entry_end.get().strip()
    email = entry_email.get().strip()

    if not start or not end or not email:
        messagebox.showerror(
            "Input error", "Please fill in start date, end date, and email."
        )
        return

    if mode == "grid":
        lat = entry_lat.get().strip()
        lon = entry_lon.get().strip()
        if not lat or not lon:
            messagebox.showerror("Input error", "Please enter latitude and longitude.")
            return
        url = build_silo_url_grid(lat, lon, start, end, email)
        file_label = f"grid_{lat}_{lon}"
    else:
        selection = station_listbox.curselection()
        if not selection:
            messagebox.showerror("Input error", "Please select a station.")
            return
        station_name = station_listbox.get(selection[0])
        station_num = stations[station_name]["number"]
        url = build_silo_url_station(station_num, start, end, email)
        file_label = f"station_{station_num}"

    try:
        print(f"DEBUG: URL used: {url}")
        resp = requests.get(url)
        if resp.status_code != 200 or "<html>" in resp.text.lower():
            raise Exception(f"Download failed: status {resp.status_code}")

        data_lines = resp.text.strip().splitlines()
        data_rows = [line.split() for line in data_lines[46:] if line.strip()]

        filename = f"silo_{file_label}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data_rows)

        messagebox.showinfo("Success", f"Data saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def toggle_mode():
    if var_mode.get() == "grid":
        entry_lat.config(state="normal")
        entry_lon.config(state="normal")
        entry_search.config(state="disabled")
        station_listbox.config(state="disabled")
    else:
        entry_lat.config(state="disabled")
        entry_lon.config(state="disabled")
        entry_search.config(state="normal")
        station_listbox.config(state="normal")


# Build UI
root = tk.Tk()
root.title("SILO Data Downloader")

# Load stations
stations = load_stations("silo_station_list.csv")

var_mode = tk.StringVar(value="grid")

tk.Radiobutton(
    root,
    text="Grid Point Location",
    variable=var_mode,
    value="grid",
    command=toggle_mode,
).grid(row=0, column=0, sticky="w")
tk.Radiobutton(
    root,
    text="Selected Station",
    variable=var_mode,
    value="station",
    command=toggle_mode,
).grid(row=0, column=1, sticky="w")

tk.Label(root, text="Latitude:").grid(row=1, column=0, sticky="e")
entry_lat = tk.Entry(root)
entry_lat.grid(row=1, column=1)

tk.Label(root, text="Longitude:").grid(row=2, column=0, sticky="e")
entry_lon = tk.Entry(root)
entry_lon.grid(row=2, column=1)

tk.Label(root, text="Search Station:").grid(row=3, column=0, sticky="e")
entry_search = tk.Entry(root, state="disabled")
entry_search.grid(row=3, column=1, sticky="we")
entry_search.bind("<KeyRelease>", update_station_list)

tk.Label(root, text="Station List:").grid(row=4, column=0, sticky="ne")
frame_station = tk.Frame(root)
frame_station.grid(row=4, column=1, sticky="we")
scrollbar = tk.Scrollbar(frame_station, orient="vertical")
station_listbox = tk.Listbox(
    frame_station, yscrollcommand=scrollbar.set, height=8, width=35
)
scrollbar.config(command=station_listbox.yview)
scrollbar.pack(side="right", fill="y")
station_listbox.pack(side="left", fill="both")

# Populate full list at start
for name in stations:
    station_listbox.insert("end", name)
station_listbox.config(state="disabled")

tk.Label(root, text="Start date (YYYYMMDD):").grid(row=5, column=0, sticky="e")
entry_start = tk.Entry(root)
entry_start.grid(row=5, column=1)

tk.Label(root, text="End date (YYYYMMDD):").grid(row=6, column=0, sticky="e")
entry_end = tk.Entry(root)
entry_end.grid(row=6, column=1)

tk.Label(root, text="Email:").grid(row=7, column=0, sticky="e")
entry_email = tk.Entry(root)
entry_email.grid(row=7, column=1)

tk.Button(root, text="Download Data", command=download_data).grid(
    row=8, column=0, columnspan=2, pady=10
)

root.mainloop()
