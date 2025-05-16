# CalarmHelp

## Why

Perhaps you like to use google calendar to time block both events and tasks - however you find the 'notifications' from those calendar events to be lack luster. It just doesn't get your attention enough to be in your face, and thus actionable.
<br><br>
Perhaps then you'd like to supplement each calendar event with a separate alarm - which also means double work.
<br><br>
Then maybe you found an alarm application like (AMDroid on Android devices) which can look at selected calendars for tags of a given name (i.e. `#work` or `#home`) paired with a reminder syntax (i.e. `[10m]` or `[120m]`) and create an alarm to pair with the specified event.

A calendar title nomenclature of say: `"Take out the trash #home [10m]"` and the event itself with a start time of 8:00AM will produce an alarm titled "Take out the trash" and be set for 7:50AM.

CalarmHelp is a word jumble coming from `"Calendar"` + `"Alarm"` + `"Help"`. Calendar Alarm Help.

CalarmHelp contains an API used to trigger `GPT4o` to translate normal human speech (or an API call) with content `"At 8AM remind me to take out the trash 10 minutes early at home"` into a JSON object which contains a structured title with a value such as
`"Take out the trash @ 8AM #home [10m]"`.
<br>
<br>

This output (simplified in this readme) is passed as input to a google calendar API service, and calls the create calendar event method - and provides the needed meta data for that event's creation.
<br>

After the calendar event is created - the Android application (or application of your choice) can look at the calendar and create an alarm on your behalf based on the tags in that title + the syntax for lead time for a reminder of that alarm.

## Setting up your project

### Requirements
- [Python >= 3.10](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/)
<br>

### Optional Requirements
- The following is required for working with docker and deploying to Google Cloud:
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/install/)
  - [gcloud CLI](https://cloud.google.com/sdk/docs/install)

_________________
### Installation

1. Make sure you have Python and Poetry installed on your system. If not, follow the instructions in the links above.
<br>

2. Clone this repository to your local machine:

```shell
git clone https://github.com/your-username/calarmHelp.git
```
<br>

3. Navigate to the project directory:

```shell
cd calarmHelp
```
<br>

4. Install the project dependencies using Poetry:

```shell
poetry install
```
<br>

5. Create an environment file

```shell
touch .env
```
<br>

6. Add the following environment variables, with values, to the `.env` file.

```.env
  OPENAI_API_KEY=<Refer to OpenAI Docs>
  ORIGINS=<A string which defines origins for CORS middleware>
  CALENDAR_ID=<The calendar ID you want to use>
  GOOGLE_APPLICATION_CREDENTIALS=<to the location of your google credentials file>
```

See [How Application Default Credentials Work](https://cloud.google.com/docs/authentication/application-default-credentials)

See [OpenAI API Keys](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)

### IMPORTANT: Accessing the Calendar with a Service Account
Find your `CALENDAR_ID` by going to your Google Calendar, clicking on the three dots next to the calendar you want to use, and selecting `Settings and Sharing`. The `CALENDAR_ID` will be listed under `Integrate Calendar`.

Ensure the calendar is shared with the service account by following these steps:

In the same Settings and sharing section, under "Share with specific people or groups," add the service account's email.
Assign the "Make changes and manage sharing" permissions.

Otherwise, the service account will not be able to access the calendar. And this application will not be able to create events on your behalf.

<br>

_________________

## Building and running your application
### Locally on your machine
The advantage of running your application locally is that you can make changes to your application and see the changes immediately.

When you're ready to run locally:
Ensure you're in the root directory of your project and run the following commands:

```
poetry run start

# alias for: `poetry run python calarmhelp/main.py`
```

Your application will be available at http://localhost:8000.
_________________

### Locally with Docker
The advantage of running your application in Docker is that you can ensure that your application runs the same way locally as it does in the cloud.

When you're ready to run locally, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:8000.
_________________

## Scripts
The commands are defined in the `tool.poetry.scripts` section of the `pyproject.toml` file for inclusion in the application. 

The scripts themselves are defined in the `calarmhelp/scripts` directory.

##### To create a new script:
1. Create a new file (named after the script) in the `calarmhelp/scripts` directory.
2. Add the script to the `tool.poetry.scripts` section of the `pyproject.toml` file.
3. Run `poetry install` to install the new script.
4. Run the script by running `poetry run <script-name>`.

### Commands:

#### Start:
To start your application, run:

`poetry run start`

For Running locally with Docker [click here](README.Docker.md#locally-with-docker) or see the [Docker-Start](#Docker-Start) section below.
<br>
<br>

#### Docker-Start:
To start your application with Docker, run:

`poetry run docker-start`
<br>
<br>

#### Docker-Build:
To build your application with Docker, run:

`poetry run docker-build <image-tag>`
<br>
<br>

#### Docker-Push:
To push your application with Docker, run:

`poetry run docker-push <image-tag>`
<br>
<br>

#### Deploy-App
To deploy your application to Google Cloud, run:

`poetry run deploy-app <tag-name>`

Where `<tag-name>` becomes part of your image name in the format:
`gcr.io/calarmhelp/calarmhelp:<tag-name>`

Examples:
- `poetry run deploy-app latest` → Creates image `gcr.io/calarmhelp/calarmhelp:latest`
- `poetry run deploy-app v1.0` → Creates image `gcr.io/calarmhelp/calarmhelp:v1.0`
- `poetry run deploy-app test-build` → Creates image `gcr.io/calarmhelp/calarmhelp:test-build`

##### Important
This command is comprehensive and will:
1. Build the Docker image with your specified tag
2. Push the image to Google Container Registry
3. Deploy the application to Google Cloud Run
4. Update the traffic to route to the new revision

Note: Use simple tag names without special characters or multiple colons.
<br>
<br>

#### Linting:
To lint your code, run:

`poetry run precommit`

The linting step will also happen automatically before you commit your code.

_________________

### References
- [Run locally with Docker](README.Docker.md#locally-with-docker)
- [Deploy to Docker to Google Cloud](README.Docker.md#deploying-to-google-cloud)
