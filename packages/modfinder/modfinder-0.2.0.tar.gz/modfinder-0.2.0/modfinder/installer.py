import os, zipfile, site, shutil

def install_wheel(wheel_path, cleanup=True):
    print(f"Installing wheel: {wheel_path}")
    temp_dir = os.path.join(os.getcwd(), "_modfinder_temp")
    with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    site_packages = site.getusersitepackages()
    dist_info_path = None

    for item in os.listdir(temp_dir):
        src = os.path.join(temp_dir, item)
        dst = os.path.join(site_packages, item)

        if os.path.exists(dst):
            print(f"Skipped: {item} (already exists)")
        else:
            shutil.move(src, dst)
            print(f"Installed: {item}")

        if item.endswith(".dist-info"):
            dist_info_path = dst

    shutil.rmtree(temp_dir)
    print("Installation complete!")

    # ✅ Delete the wheel file if cleanup is enabled
    if cleanup and os.path.exists(wheel_path):
        os.remove(wheel_path)
        print(f"Deleted wheel file: {wheel_path}")

    # (Optional) parse dependencies here and install them recursively