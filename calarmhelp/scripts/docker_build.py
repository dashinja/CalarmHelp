import argparse
import subprocess

default_docker_repo = "gcr.io/calarmhelp/"


def arg_parser():
    parser = argparse.ArgumentParser(description="Docker build script")
    parser.add_argument("docker_image_name", type=str, help="Name of the docker image")
    return parser.parse_args()


def runner(service_name):
    command = [
        "docker",
        "build",
        "-t",
        f"{default_docker_repo}{service_name}",
        ".",
    ]
    subprocess.run(command)


def run():
    args = arg_parser()
    runner(args.docker_image_name)


if __name__ == "__main__":
    run()
