from setuptools import setup
import os

print("[cadens_package] Install-time script is running!")

log_path = os.path.join(os.getcwd(), "cadens_install_log.txt")
with open(log_path, "w") as f:
    f.write("cadens_package was installed successfully.\n")

setup()
