import os
import string

import requests


def fetch_all_stations():
    base_url = "https://www.longpaddock.qld.gov.au/cgi-bin/silo/PatchedPointDataset.php"
    save_path = os.path.join(os.getcwd(), "silo_station_list.csv")

    with open(save_path, "w") as f:
        for frag in string.ascii_uppercase:
            url = f"{base_url}?format=name&nameFrag={frag}"
            response = requests.get(url)

            if response.status_code == 200:
                lines = response.text.strip().splitlines()
                for line in lines:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        station_num = parts[0].strip()
                        name = parts[1].strip()
                        lat = parts[2].strip()
                        lon = parts[3].strip()
                        f.write(f"{station_num},{name},{lat},{lon}\n")
                print(f"✅ Fetched stations for fragment '{frag}'")
            else:
                print(
                    f"❌ Failed for fragment '{frag}' - status {response.status_code}"
                )

    print(f"🎉 Full station list saved to: {save_path}")


if __name__ == "__main__":
    fetch_all_stations()
