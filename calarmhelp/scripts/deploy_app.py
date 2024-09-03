import os
import subprocess
from dotenv import load_dotenv
from .docker_build import docker_build
from .docker_push import docker_push

load_dotenv()


def run():
  """
  Runs the deployment process for the Docker service.

  This function performs the following steps:
  1. Builds the Docker image.
  2. Pushes the Docker image to the registry.
  3. Deploys the artifact using the service name.
  4. Updates the traffic configuration for the Cloud Run service.

  """

  print("Building Docker image for the application...")
  service_name = docker_build()
  
  print("Pushing Docker image to the registry...")
  docker_push(service_name)

  print(f"Deploying {service_name} to Cloud Run...")
  artifact_deploy(service_name)

  print("Updating traffic configuration for Cloud Run to send all to most recent revision...")
  cloud_run_traffic_update()


def cloud_run_traffic_update():
  """
  Updates the traffic to the latest revision of the 'calarm-help-should' service in the 'us-east1' region using the 'gcloud' command.

  Parameters:
  None

  Returns:
  None
  """
  # Update traffic to the latest revision
  updateTrafficScript = [
    "gcloud", "run", "services", "update-traffic", "calarm-help-should",
    "--to-latest", "--region=us-east1"
  ]

  subprocess.run(updateTrafficScript, check=True)

def artifact_deploy(service_name: str):
    """
    Deploy the artifact to Google Cloud Run.
    Args:
      service_name (str): The name of the service.
    Raises:
      EnvironmentError: If any of the required environment variables are not set.
    """
    required_env_vars = [
    'ORIGINS', 'OPENAI_API_KEY', 'HAYSTACK_CONTENT_TRACING_ENABLED',
    'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_HOST',
    'TELEMETRY_ENABLED', 'CALENDAR_ID'
  ]

    for var in required_env_vars:
      if os.getenv(var) is None:
        raise EnvironmentError(f"Environment variable {var} is not set")

    set_image = f"--image=gcr.io/calarmhelp/calarmhelp:{service_name}"
    
    # Construct the deploy script
    deployScript = [
      "gcloud", 
      "run",
      "deploy", 
      "calarm-help-should",
      set_image,
      f"--set-env-vars=ORIGINS={os.getenv('ORIGINS')}",
      f"--set-env-vars=OPENAI_API_KEY={os.getenv('OPENAI_API_KEY')}",
      f"--set-env-vars=HAYSTACK_CONTENT_TRACING_ENABLED={os.getenv('HAYSTACK_CONTENT_TRACING_ENABLED')}",
      f"--set-env-vars=LANGFUSE_SECRET_KEY={os.getenv('LANGFUSE_SECRET_KEY')}",
      f"--set-env-vars=LANGFUSE_PUBLIC_KEY={os.getenv('LANGFUSE_PUBLIC_KEY')}",
      f"--set-env-vars=LANGFUSE_HOST={os.getenv('LANGFUSE_HOST')}",
      f"--set-env-vars=TELEMETRY_ENABLED={os.getenv('TELEMETRY_ENABLED')}",
      f"--set-env-vars=CALENDAR_ID={os.getenv('CALENDAR_ID')}",
      "--region=us-east1",
      "--project=calarmhelp"
    ]

    # Run the deploy script
    subprocess.run(deployScript, check=True)
  
if __name__ == "__main__":
  run() 