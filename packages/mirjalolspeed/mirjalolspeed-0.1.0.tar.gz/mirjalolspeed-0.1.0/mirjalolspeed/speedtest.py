import time
import requests

def download_speed_live(url="https://speed.hetzner.de/100MB.bin", chunk_size=1024*1024):
    print("Download test started...")

    response = requests.get(url, stream=True)
    downloaded = 0
    start = time.time()

    for chunk in response.iter_content(chunk_size=chunk_size):
        downloaded += len(chunk)
        duration = time.time() - start
        speed_mbps = (downloaded * 8) / (duration * 1024 * 1024)
        print(f"\rSpeed: {speed_mbps:.2f} Mbps", end="")
    
    print("\nDone.")
