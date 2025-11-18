from setuptools import setup
import os

print("[cadens_package] Install-time script is running!")

with open("cadens_install_log.txt", "w") as f:
    f.write("cadens_package was installed successfully.\n")

setup()
