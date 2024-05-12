import subprocess
import os


PORT = int(os.getenv("PORT", 8000))
# Defaults to 8000 if PORT is not set.


def run():
    command = ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", str(PORT)]
    subprocess.run(command)


if __name__ == "__main__":
    run()
