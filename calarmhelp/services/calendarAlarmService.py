from haystack import Pipeline

from datetime import datetime

from calarmhelp.services.util.util import (
    CalendarAlarmResponse,
    GoogleCalendarInfoInput,
)

from haystack.core.component import component
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

from ..templates.googleCalendarFeeder import (
    google_calendar_feeder2,
)


def create_alarm_readout(input: CalendarAlarmResponse) -> str:
    """Provides the 'description' field for google calendar

    Args:
        input (dict): The input dictionary containing alarm information.

    Returns:
        str: A string that describes the alarm in a format that Google Calendar can understand.
    """

    month = input.event_time.strftime("%B")
    day_number = input.event_time.strftime("%d")
    day_of_week = input.event_time.strftime("%A")
    time_of_day = input.event_time.strftime("%I:%M %p")
    locationCondition = f"{(' at ' + input.location) if input.location else ''}"

    # Take care with format. Everything, even spacing - is intentional.
    return f"{input.name} @ {time_of_day}{locationCondition} on {day_of_week} {month} {day_number} #{input.category.name.lower()} [{input.lead_time}m]"


@component
class JSONValidator:
    @component.output_types(properties_to_validate=list[str], json=str)
    def run(self, properties: list[str]):
        if "DONE" in properties[0]:
            return {"json": properties[0].replace("Done", "")}
        else:
            return {"properties_to_validate": properties[0]}


@component
class CalendarAlarmServicePipeline:
    """
    Pipeline for processing calendar alarm service. Requires OPENAI_API_KEY in a `.env` file in root directory to function properly.

    #### Attributes:
    ```
    _generator (OpenAIGenerator):
    ```The OpenAIGenerator instance.
    ```
    _pipeline (Pipeline):
    ```The Pipeline instance.
    #### Methods:
        ```
        run(input: str) -> GoogleCalendarInfoInput:
        ```
        Runs the pipeline to process the input and returns `GoogleCalendarInfoInput`.

        Args:
        ```
        input (str):
        ``` The input string.
        Returns:
            GoogleCalendarInfoInput: The processed GoogleCalendarInfoInput.
    """

    def __init__(self):
        self._generator = OpenAIGenerator(
            model="gpt-4o",
            generation_kwargs={"temperature": 0},
        )
        self._pipeline = Pipeline(max_loops_allowed=20)

    def cleanJsonOutput(self, jsonOutput: str) -> str:
        jsonOutput = jsonOutput.replace("```json", "")
        jsonOutput = jsonOutput.replace("```", "")
        return jsonOutput

    @component.output_types(output=GoogleCalendarInfoInput)
    def run(self, input: str) -> GoogleCalendarInfoInput:
        modified_input = {
            "user_input": input,
            "current_time": datetime.now().isoformat(),
        }

        prompt_builder = PromptBuilder(
            template=google_calendar_feeder2,
        )
        generator = self._generator
        json_validator = JSONValidator()

        self._pipeline.add_component("prompt_builder", prompt_builder)
        self._pipeline.add_component("generator", generator)
        self._pipeline.add_component("validator", json_validator)

        self._pipeline.connect("prompt_builder.prompt", "generator.prompt")
        self._pipeline.connect("generator.replies", "validator.properties")
        self._pipeline.connect(
            "validator.properties_to_validate", "prompt_builder.properties_to_validate"
        )

        results = self._pipeline.run(
            data={
                "prompt_builder": {"input": modified_input},
            }
        )

        jsonOutput: str = results["validator"]["json"].replace("DONE", "")

        jsonOutput = self.cleanJsonOutput(jsonOutput)

        parsedJsonObject = CalendarAlarmResponse.model_validate_json(jsonOutput)

        return GoogleCalendarInfoInput(
            response=create_alarm_readout(parsedJsonObject), theJson=parsedJsonObject
        )


