from pprint import pprint
import google.auth
from google.auth.transport.requests import AuthorizedSession, Request
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

Scopes = [
    'https://www.googleapis.com/auth/script.projects',
    "https://www.googleapis.com/auth/script.deployments",
    "https://www.googleapis.com/auth/script.deployments.readonly",
    "https://www.googleapis.com/auth/script.metrics",
    "https://www.googleapis.com/auth/script.processes",
    "https://www.googleapis.com/auth/script.projects.readonly",
    "https://www.googleapis.com/auth/script.external_request",

]


def googleCalendarServiceScript(user_input):
    credentials, _ = google.auth.default(
        scopes=Scopes,
        quota_project_id='calarmhelp'
    )

    # Refresh credentials if they are invalid
    if not credentials.valid:
        credentials.refresh
        credentials.refresh(Request())
    scriptService = build('script', 'v1',
                          credentials=credentials)

    # script_id='AKfycbxQFBeuXD3t6pvU0dSl4AcNntn3UyTlKPyhZ1RRhwGXcf5wRm4zKDr_k4JdEiulV4zo'
    script_id = 'AKfycbw5CFyqyq0-m4P3naNhRST0STImUQHlTcFrt14-5PY'
    api_url = f'https://script.googleapis.com/v1/scripts/{script_id}:run'

    request_body = {
        'function': 'doGet',
        'parameters': [user_input],
        'devMode': True
    }

    # print('request_body: ', request_body)
    try:
        script = scriptService.scripts()
        response = script.run(scriptId=script_id, body=request_body).execute()
        # response = request.execute()
        if "error" in response:
            # The API executed, but the script returned an error.
            # Extract the first (and only) set of error details. The values of
            # this object are the script's 'errorMessage' and 'errorType', and
            # a list of stack trace elements.
            error = response["error"]["details"][0]
            print(f"Script error message: {0}.{format(error['errorMessage'])}")

            if "scriptStackTraceElements" in error:
                # There may not be a stacktrace if the script didn't start
                # executing.
                print("Script error stacktrace:")
                for trace in error["scriptStackTraceElements"]:
                    print(f"\t{0}: {1}.{format(trace['function'], trace['lineNumber'])}")
        else:
            responseObject = response
            body = json.loads(responseObject)['body']
            print("body")
            pprint(body)
            finalOutput = json.loads(body)['parameters'][0]
            print("finalOutput")
            pprint(finalOutput)
            finalOutput2 = json.loads(finalOutput['output'])
            print("finalOutput2")
            pprint(finalOutput2)

            return finalOutput2

    except HttpError as error:
        # The API encountered a problem before the script started executing.
        print(f"An error occurred: {error}")
        print(error.content)

    if __name__ == "__googleCalendarServiceScript__":
        googleCalendarServiceScript(user_input)
