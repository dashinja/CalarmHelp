import subprocess

def run():
  command = [
    "poetry",
    "run",
    "pre-commit",
    "run",
    "--all-files",
  ]

  subprocess.run(command)
  
  if __name__ == "__main__":
    run()