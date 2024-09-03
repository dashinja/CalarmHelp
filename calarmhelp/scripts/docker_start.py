import subprocess


def run():
    command = [
        "docker",
        "compose",
        "up",
        "--build",
    ]
    subprocess.run(command)
