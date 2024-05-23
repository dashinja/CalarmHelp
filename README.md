# CalarmHelp

## Installation

1. Make sure you have Python and Poetry installed on your system. If not, you can install them by following the official documentation:
  - Python: https://www.python.org/downloads/
  - Poetry: https://python-poetry.org/docs/#installation

2. Clone this repository to your local machine:

  ```shell
  git clone https://github.com/your-username/calarmHelp.git
  ```

3. Navigate to the project directory:

  ```shell
  cd calarmHelp
  ```

4. Install the project dependencies using Poetry:

  ```shell
  poetry install
  ```

5. Create an environment file
  ```shell
  touch .env
  ```

6. Add the following environment variables, with values, to the `.env` file.

  ```.env     
    OPENAI_API_KEY=<Refer to OpenAI Docs>
    export LANGCHAIN_TRACING_V2=<Refer to LangSmith Docs>
    export LANGCHAIN_API_KEY=<Refer to LangSmith Docs>
    ORIGINS=<A string which defines origins for CORS middleware>
  ```

  [OpenAI API Keys](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)
  <br>
  [LangSmith Documentation](https://docs.smith.langchain.com/#3-set-up-your-environment)

7. TODO: Add Information on Gcloud Credentials

## Usage

To start the application, run the following command:
  ```shell
  poetry run start
  ```
