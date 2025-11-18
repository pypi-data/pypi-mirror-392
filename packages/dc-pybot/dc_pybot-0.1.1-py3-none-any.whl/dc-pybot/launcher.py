import sys
import os
import subprocess
import requests

prefix = '[PyBot] '

def launch():
    if not sys.version_info >= (3, 12):
        raise RuntimeError("PyBot requires Python >= 3.12")

    print(f"{prefix}Fetching bot code...")
    url = "https://pybotapi.javanodes.in/get_release"
    code = requests.get(url).text

    cwd = os.getcwd()
    bot_file = os.path.join(cwd, "main.py")

    print(f"{prefix}Saving main.py to: {cwd}")
    with open(bot_file, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"{prefix}main.py saved.")
    print(f"{prefix}Launching main.py...")

    subprocess.run([sys.executable, "main.py"])
