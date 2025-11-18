from .downloader import download_package
from .installer import install_wheel

def install(package_name):
    print(f"Installing {package_name}...")
    wheel_path = download_package(package_name)
    print(f"Downloaded: {wheel_path}")
    install_wheel(wheel_path)
    return True