import argparse
import subprocess

default_docker_repo = "gcr.io/calarmhelp/calarmhelp:"


def arg_parser():
    """
    Docker push script

    Args:
      docker_image_name (str): Name of the docker image

    Returns:
      argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Docker push script")
    parser.add_argument("docker_image_name", type=str, help="Name of the docker image")
    return parser.parse_args()


def runner(service_name):
    """
    Pushes the Docker image for the specified service to the default Docker repository.

    Args:
      service_name (str): The name of the service.

    Returns:
      str: The name of the service.

    """
    command = [
        "docker",
        "push",
        f"{default_docker_repo}{service_name}",
    ]
    subprocess.run(command)
    return service_name


def docker_push(service_name=None):
    """
    Specific for ease of use in the `deploy_app` script.
    Pushes the Docker image for the specified service to the Docker registry.

    Args:
      service_name (str, optional): The name of the service. If not provided, all services will be pushed.

    Returns:
      The result of the push operation.

    """
    return run(service_name)


def run(service_name=None):
    """
    Run the docker_push script.

    Args:
      service_name (str, optional): The name of the service. Defaults to None. if service_name is None as a function argument, the service_name will be taken from the command line arguments.

    Returns:
      None
    """
    args = arg_parser()
    return runner(service_name or args.docker_image_name)


if __name__ == "__main__":
    run()
