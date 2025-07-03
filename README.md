# SILO Weather Data Tools
User guide
https://charlesdarwinuni-my.sharepoint.com/:w:/r/personal/s374211_students_cdu_edu_au/_layouts/15/Doc.aspx?sourcedoc=%7BD56C1C45-5030-42E0-8E3C-03513CA9D372%7D&file=User%20Guide_RINA_Download&Analyse_SILO.docx=&wdOrigin=TEAMS-MAGLEV.undefined_ns.rwc&action=default&mobileredirect=true

This repository provides a set of GUI tools to help users interact with the [SILO climate data API](https://www.longpaddock.qld.gov.au/silo/). The tools are written in Python and support:

- **Station list downloader**
- **Weather data downloader (by coordinates or station name)**
- **Summarizer for calculating monthly statistics (mean/sum) and exporting to Excel**

## Contents

### 1. `fetch_station_list.py`
Script to fetch all available weather stations and export them to `silo_station_list.csv`.

### 2. `silo_data_downloader.py`
Tkinter GUI for downloading SILO weather data. Users can choose between:
- Grid location (lat/lon)
- Station name (search and scroll interface)

### 3. `silo_data_summarizer.py`
Tkinter GUI for:
- Loading CSV or Excel files with SILO-formatted data
- Selecting multiple parameters (e.g., temperature, PET, etc.)
- Choosing summary method (monthly **average** or **total**)
- Exporting to an Excel workbook with one sheet per parameter

---

## 📦 Installation

Install Python 3.8 or newer, then run:

```bash
pip install -r requirements.txt
