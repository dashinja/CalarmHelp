import subprocess


def run():
    command = ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    subprocess.run(command)

    if __name__ == "__main__":
        run()
