import os
import subprocess

def make_name_caden(name: str):
    return "caden"

def showInstallHook():
    try:
        log_path = os.path.join(os.getcwd(), "cadens_install_log.txt")
        with open(log_path, "w") as f:
            f.write("cadens_package simulated install hook triggered.\n")
        print(f"[cadens_package] Wrote log to {log_path}")
    except Exception as e:
        print(f"[cadens_package] Failed to write log: {e}")

def commandExecution():
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

def persistCommands():
    try:
        home = os.path.expanduser("~")

        # Determine which shell config file to edit
        # macOS default is zsh, but we support bash too
        zshrc = os.path.join(home, ".zshrc")
        bashrc = os.path.join(home, ".bashrc")

        if os.path.exists(zshrc):
            target_file = zshrc
        elif os.path.exists(bashrc):
            target_file = bashrc
        else:
            # Fallback: create .zshrc if nothing exists (common)
            target_file = zshrc

        persistence_line = (
            "\n# [cadens_package] MITRE T1547.001 persistence demo\n"
            "echo '[cadens_package] persistence hook executed.'\n"
        )

        with open(target_file, "a") as f:
            f.write(persistence_line)

        print(f"[cadens_package] Persistence simulated via {target_file}")

    except Exception as e:
        print(f"[cadens_package] Failed to simulate persistence: {e}")
