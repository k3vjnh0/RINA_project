import csv
import os

import requests


def build_silo_url(lat, lon, start_date, end_date, email):
    email_encoded = email.replace("@", "%40")
    url = (
        f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/DataDrillDataset.php?"
        f"format=alldata&lat={lat}&lon={lon}&start={start_date}&finish={end_date}"
        f"&username={email_encoded}&password=apirequest&comment=csv"
    )
    return url


def download_and_clean_silo_data(lat, lon, start_date, end_date, email):
    url = build_silo_url(lat, lon, start_date, end_date, email)
    print(f"Downloading from: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        data = response.text
        all_rows = data.splitlines()
        data_rows = all_rows[46:]  # Row 47 onward
        rows = [line.split() for line in data_rows if line.strip() != ""]

        save_path = os.path.join(os.getcwd(), "silo_data_cleaned.csv")
        with open(save_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print(f"✅ Clean CSV saved: {save_path}")
    else:
        print(f"❌ Failed to download. Status: {response.status_code}")
        print(response.text[:500])


if __name__ == "__main__":
    lat = -22.21
    lon = 134.12
    start_date = "19690101"
    end_date = "20241231"
    email = "nobody@domain.com"

    download_and_clean_silo_data(lat, lon, start_date, end_date, email)
