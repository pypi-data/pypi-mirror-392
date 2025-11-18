from .core import make_name_caden
import os
import subprocess

__all__ = ["make_name_caden"]

print("[cadens_package] Import hook triggered (simulating supply-chain compromise).")

try:
    log_path = os.path.join(os.getcwd(), "cadens_install_log.txt")
    with open(log_path, "w") as f:
        f.write("cadens_package simulated install hook triggered.\n")
    print(f"[cadens_package] Wrote log to {log_path}")
except Exception as e:
    print(f"[cadens_package] Failed to write log: {e}")

try:
    print("[cadens_package] Simulating command execution: running 'ls'")

    result = subprocess.run(
        ["ls"],
        capture_output=True,
        text=True
    )
    
    command_log = os.path.join(os.getcwd(), "cadens_command_output.txt")
    with open(command_log, "w") as f:
        f.write("Simulated command executed: ls\n")
        f.write("Output:\n")
        f.write(result.stdout)

    print(f"[cadens_package] Command output saved to {command_log}")

except Exception as e:
    print(f"[cadens_package] Error during command simulation: {e}")
