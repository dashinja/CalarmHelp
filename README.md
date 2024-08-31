# CalarmHelp

## Why

Perhaps you like to use google calendar to time block both events and tasks - however you find the 'notifications' from those calendar events to be lack luster. It just doesn't get your attention enough to be in your face, and thus actionable.
<br><br>
Perhaps then you'd like to supplement each calendar event with a separate alarm - which also means double work.
<br><br>
Then maybe you found an alarm application like (AMDroid on Android devices) which can look at selected calendars for tags of a given name (i.e. `#work` or `#home`) paired with a reminder syntax (i.e. `[10m]` or `[120m]`) and create an alarm to pair with the specifid event.

A calendar title nomenclature of say: `"Take out the trash. #home [10m]"` and the event itself with a start time of 8:00AM will produce an alarm titled "Take out the trash" and be set for 7:50AM.

CalarmHelp is a word jumble coming from `"Calendar"` + `"Alarm"` + `"Help"`. Calendar Alarm Help.

CalarmHelp contains an API used to trigger `GPT4o` to translate normal human speech like `"At 8AM remind me to take out the trash 10 minutes early at home"` into a JSON object which contains a structured title with a value such as
`"Take out the trash @ 8AM #home [10m]"`.
<br><br>
This output (simplified in this readme) is passed as input to a google calendar API service, and calls the create calendar event method - and provides the needed meta data for that event's creation.
<br><br>
After the calendar event is created - the Android application can look at the calendar and create an alarm on your behalf based on the tags in that title + the syntax for lead time for a reminder of that alarm.

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
  ORIGINS=<A string which defines origins for CORS middleware>
```

[OpenAI API Keys](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)
<br>

7. Add GCP Credentials
   #TODO#

## Usage

To start the application, run the following command:

```shell
poetry run start
```
