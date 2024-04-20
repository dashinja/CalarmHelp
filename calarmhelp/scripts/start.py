import subprocess


def run():
    command = ["uvicorn", "main:app", "--reload"]
    subprocess.run(command)

    if __name__ == "__main__":
        run()
