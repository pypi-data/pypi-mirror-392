from .core import make_name_caden
import os

__all__ = ["make_name_caden"]

print("[cadens_package] Install-time script is running!")

log_path = os.path.join(os.getcwd(), "cadens_install_log.txt")
with open(log_path, "w") as f:
    f.write("cadens_package was installed successfully.\n")