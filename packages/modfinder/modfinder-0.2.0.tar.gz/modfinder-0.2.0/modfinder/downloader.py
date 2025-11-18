import requests
import os
import sys
import platform

def download_package(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Package {package_name} not found on PyPI.")

    data = response.json()

    # Try to find a wheel matching current Python version/platform
    py_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
    arch = platform.system().lower()

    chosen_file = None
    for file in data["urls"]:
        if file["filename"].endswith(".whl"):
            # crude filter: prefer universal wheels or matching python version
            if "none-any" in file["filename"] or py_version in file["filename"]:
                chosen_file = file
                break

    if not chosen_file:
        raise Exception("No compatible wheel file found.")

    download_url = chosen_file["url"]
    filename = chosen_file["filename"]

    print(f"Downloading {filename} from {download_url}...")
    response = requests.get(download_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Downloaded: {filename}")
    return os.path.abspath(filename)