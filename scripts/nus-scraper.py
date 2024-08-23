import os

import requests


tid_high = ["00010000", "00010001", "00010005"]
types = ["43", "44", "45", "46", "47", "48", "4A", "4C", "4D", "4E", "50", "51", "52", "53", "57", "58"]
regions = ["45", "4A", "4B", "50"]


for tid in tid_high:
    print(f"Starting scrape for TID high {tid}...")

    if os.path.exists(f"{tid}.log"):
        os.remove(f"{tid}.log")
    log = open(f"{tid}.log", "a")

    for ttype in types:
        print(f"Scraping titles of type: {ttype}")
        for title in range(0, 65536):
            for region in regions:
                request = requests.get(url=f"http://ccs.cdn.wup.shop.nintendo.net/ccs/download/{tid}{ttype}{title:04X}{region}/tmd", headers={'User-Agent': 'wii libnup/1.0'}, stream=True)
                if request.status_code == 200:
                    print(f"Found valid TID: {tid}{ttype}{title:04X}{region}")
                    log.write(f"{tid}{ttype}{title:02X}{region}")
                else:
                    print(f"Invalid TID: {tid}{ttype}{title:04X}{region}")
                    pass
                request.close()
    log.close()
