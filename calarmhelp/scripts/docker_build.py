import argparse
import subprocess

default_docker_repo = "gcr.io/calarmhelp/calarmhelp:"
default_docker_repo = "gcr.io/calarmhelp/calarmhelp:"


def arg_parser():
    """
    Docker build script

    Args:
        docker_image_name (str): Name of the docker image

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    """
    Docker build script

    Args:
        docker_image_name (str): Name of the docker image

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Docker build script")
    parser.add_argument("docker_image_name", type=str, help="Name of the docker image")
    return parser.parse_args()


def runner(service_name):
    """
    Builds a Docker image for the specified service.

    Args:
        service_name (str): The name of the service.

    Returns:
        str: The name of the service.

    """
    """
    Builds a Docker image for the specified service.

    Args:
        service_name (str): The name of the service.

    Returns:
        str: The name of the service.

    """
    command = [
        "docker",
        "build",
        "-t",
        f"{default_docker_repo}{service_name}",
        ".",
    ]
    subprocess.run(command)
    return service_name


def docker_build(service_name=None):
    """
    Specific for ease of us in the `deploy_app` script.
    Builds a Docker image using the specified parameters.

    Parameters:
        None

    Returns:
        None
    """
    return run()


def run(service_name=None):
    """
    Run the docker_build script.

    Returns:
        str: The name of the docker image.
    """
    args = arg_parser()
    return runner(service_name or args.docker_image_name)


if __name__ == "__main__":
    run()
