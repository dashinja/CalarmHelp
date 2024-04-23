from cloudFunctions.event.services.calendarAlarmService import CalendarAlarmService
from cloudFunctions.event.services.googleCalendarService import googleCalendarServiceScript
import functions_framework
from pydantic import BaseModel

class CreateAlarmRequest(BaseModel):
    input: str

@functions_framework.http
def hello_get(request):
    request.get_json()
    print("Calling Calendar Alarm Service")

    request_json = request.get_json()
    if request_json and 'input' in request_json:
        user_input = request_json['input']

    calendarService = CalendarAlarmService()
    calendarServiceResponse = calendarService.create_alarm_json(user_input)

    print("Parsing Calendar Alarm Service Response")
    parsedCalendarServiceResponse = json.loads(calendarServiceResponse) # type: ignore

    print("Passing to Google Calendar Service")
    endgame = googleCalendarServiceScript(parsedCalendarServiceResponse)

    response = calendarServiceResponse

    print("Returning from Google Calendar Service")
    return response

    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    return 'Hello World!'