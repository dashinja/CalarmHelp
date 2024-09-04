import os
from pathlib import Path
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.core.component import component
from haystack_integrations.components.connectors.langfuse import LangfuseConnector

from calarmhelp.services.util.util import (
    CalendarAlarmResponse,
    GoogleCalendarInfoInput,
    GoogleCalendarResponse,
)

load_dotenv()

# Load the template file
template_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../templates/googleCalendarFeeder.jinja",
)

with open(template_file_path, "r") as file:
    template_content = file.read()


def create_pipeline_chart(pipeline: Pipeline, file_name: str = "pipeline.png"):
    """
    Create a pipeline chart.

    Args:
        pipeline (Pipeline): The pipeline object to be drawn.
        file_name (str, optional): The name of the output file. Defaults to "pipeline.png".
    """
    if os.getenv("ENVIRONMENT") not in ["production", "docker"]:
        pipeline.draw(
            Path(
                os.path.join(os.path.dirname(os.path.abspath(__file__))),
                f"../architecture/pipelines/{file_name}",
            )
        )


def create_pipeline_yml(pipeline: Pipeline, file_name: str = "pipeline.yml"):
    """
    Creates a YAML file for the given pipeline.

    Args:
        pipeline (Pipeline): The pipeline object to be dumped into the YAML file.
        file_name (str, optional): The name of the YAML file. Defaults to "pipeline.yml".
    """
    with open(file_name, "w") as file:
        pipeline.dump(file)


def create_alarm_readout(input: CalendarAlarmResponse) -> str:
    """Provides the 'description' field for google calendar

    Args:
        input (CalendarAlarmResponse): The input object containing alarm information.

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
    """
    This class provides a JSON validation functionality.

    Methods:
    - run(properties: list[str]) -> dict: Validates the given properties and returns a dictionary with the validation results.

    Attributes:
    - None
        Validates the given properties and returns a dictionary with the validation results.

        Parameters:
        - properties (list[str]): A list of properties to be validated.

        Returns:
        - dict: A dictionary containing the validation results. If the first property contains the string "DONE", the dictionary will have the key "json" with the modified property value. Otherwise, the dictionary will have the key "properties_to_validate" with the original property value.

        Example:
        ```
        validator = JSONValidator()
        result = validator.run(["DONE: property1"])
        print(result)  # Output: {"json": ": property1"}
        ```
    """

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

    _max_loops_allowed: int

    def __init__(self, max_loops_allowed: int = 20):
        self._generator = OpenAIGenerator(
            model="gpt-4o",
            generation_kwargs={"temperature": 0},
            api_key=Secret.from_env_var("OPENAI_API_KEY"),
        )

        self._max_loops_allowed = max_loops_allowed

        self._pipeline = Pipeline(max_loops_allowed=self._max_loops_allowed)

    def cleanJsonOutput(self, jsonOutput: str) -> str:
        """
        Cleans the given JSON output by removing the markdown code block syntax.

        Args:
            jsonOutput (str): The JSON output to be cleaned.

        Returns:
            str: The cleaned JSON output.

        """
        jsonOutput = jsonOutput.replace("```json", "")
        jsonOutput = jsonOutput.replace("```", "")
        return jsonOutput

    @component.output_types(output=GoogleCalendarInfoInput)
    def run(self, input: str) -> GoogleCalendarInfoInput | GoogleCalendarResponse:
        modified_input = {
            "user_input": input,
            "current_time": datetime.now().isoformat(),
        }

        prompt_builder = PromptBuilder(template=template_content)
        generator = self._generator
        json_validator = JSONValidator()

        self._pipeline.add_component(
            "tracer", LangfuseConnector("Calendar Alarm Service")
        )
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

        try:
            parsedJsonObject = CalendarAlarmResponse.model_validate_json(jsonOutput)

            print(f"LangFuse: {results['tracer']['trace_url']}\n")

            return GoogleCalendarInfoInput(
                response=create_alarm_readout(parsedJsonObject),
                theJson=parsedJsonObject,
            )
        except Exception as e:
            return GoogleCalendarResponse(error=f"Error in Google Calendar Service: {e}")
