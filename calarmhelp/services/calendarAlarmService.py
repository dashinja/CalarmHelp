import os
import json
import logging

import pydantic
from pydantic import ValidationError

from pathlib import Path
from datetime import datetime
from typing import Optional, Type

from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.core.component import component


from calarmhelp.services.util.util import CalendarAlarmResponse, GoogleCalendarInfoInput

from dotenv import load_dotenv

load_dotenv()

from haystack_integrations.components.connectors.langfuse import LangfuseConnector

logger = logging.getLogger("haystack")


template_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../templates/googleCalendarFeeder.jinja",
)

with open(template_file_path, "r") as file:
    template_content = file.read()


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
    @component.output_types(properties_to_validate=list[str], json=str)
    def run(self, properties: list[str]):
        if "DONE" in properties[0]:
            return {"json": properties[0].replace("Done", "")}
        else:
            return {"properties_to_validate": properties[0]}


@component
class AlternateValidator:
    def __init__(
        self, pydantic_model: Type[pydantic.BaseModel], iteration_limit: int = 20
    ):
        self.pydantic_model = pydantic_model
        self.iteration_limit = iteration_limit
        self.iteration_counter = 0

    @component.output_types(
        valid_replies=list[str],
        invalid_replies=Optional[list[str]],
        error_message=Optional[str],
    )
    def run(self, replies: list[str]) -> dict:
        self.iteration_counter += 1

        try:
            output_dict = json.loads(replies[0])
            self.pydantic_model.model_validate(output_dict)

            return {"valid_replies": replies}
        except (ValueError, ValidationError) as e:

            return {
                "invalid_replies": replies,
                "error_message": str(e),
                "iteration_limit": self.iteration_limit,
                "iteration": self.iteration_counter,
            }


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
        jsonOutput = jsonOutput.replace("```json", "")
        jsonOutput = jsonOutput.replace("```", "")
        return jsonOutput

    @component.output_types(output=GoogleCalendarInfoInput)
    def run(self, input: str) -> GoogleCalendarInfoInput:
        modified_input = {
            "user_input": input,
            "current_time": datetime.now().isoformat(),
        }

        def alternate_validation_setup():
            # Requires usage of haystackGuidedFeeder.jinja

            alternate_validator = AlternateValidator(
                pydantic_model=CalendarAlarmResponse,
                iteration_limit=self._max_loops_allowed,
            )

            pipeline = Pipeline(max_loops_allowed=self._max_loops_allowed)
            pipeline.add_component("prompt_builder", prompt_builder)
            pipeline.add_component("generator", generator)
            pipeline.add_component("alternate_validator", alternate_validator)

            pipeline.connect("prompt_builder.prompt", "generator.prompt")
            pipeline.connect("generator.replies", "alternate_validator.replies")
            pipeline.connect(
                "alternate_validator.invalid_replies", "prompt_builder.invalid_replies"
            )
            pipeline.connect(
                "alternate_validator.error_message", "prompt_builder.error_message"
            )

            results = self._pipeline.run(
                data={
                    "prompt_builder": {
                        "input": modified_input,
                        "schema": CalendarAlarmResponse,
                        "iteration": self._max_loops_allowed,
                    },
                }
            )

            return results

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

        if os.getenv("ENVIRONMENT") not in ["production", "docker"]:
            self._pipeline.draw(
                Path(
                    os.path.join(os.path.dirname(os.path.abspath(__file__))),
                    "../architecture/pipelines/calendarAlarmServicePineline.png",
                )
            )

            with open("calendarAlarmService.yml", "w") as file:
                self._pipeline.dump(file)

        results = self._pipeline.run(
            data={
                "prompt_builder": {"input": modified_input},
            }
        )

        jsonOutput: str = results["validator"]["json"].replace("DONE", "")

        jsonOutput = self.cleanJsonOutput(jsonOutput)
        parsedJsonObject = CalendarAlarmResponse.model_validate_json(jsonOutput)

        logger.info(f"\nLangFuse: {results['tracer']['trace_url']}\n")

        return GoogleCalendarInfoInput(
            response=create_alarm_readout(parsedJsonObject), theJson=parsedJsonObject
        )
