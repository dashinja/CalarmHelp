google_calendar_feeder = """{% if properties_to_validate %}
    Here was the json you were provided:
    {{input.user_input}}
    {{input.current_time}}

    Here are the properties you previously extracted:
    {{properties_to_validate[0]}}
    Are these the correct properties?
    Things to check for:
    - Properties should be exactly one of these: name, category, lead_time, event_time, event_time_end, location, error, current_time
    - Properties should be in the correct format
    - There should be no extra properties
    - There should be no missing properties
    - There should be no duplicate properties
    
    Here is the schema for the JSON that you make must meet:
        name: str = Field(description="Name of the event")
        category: Category = Field(description="Category of the event which can only be exactly one of: 'always', 'work', 'home'")
        lead_time: int = Field(description="How long before the event I should be reminded. Defaults to 30 minutes if not provided.")
        event_time: datetime = Field(description="When the event should actually happen. Always following the 'America/New_York' timezone. Assume the starting point for the year is based on the {{input.current_time}}")
        event_time_end: datetime = Field(description="When the event should actually end. Always following the 'America/New_York' timezone. Assume the starting point for the year is based on the {{input.current_time}}")
        location: str = Field(description="Location of event, if provided")
        error: bool = Field(default=False, description="If there was an error in the input then True. Otherwise, False.")
        current_time: datetime = Field(description="The current time. Always following the 'America/New_York' timezone. Assume the starting point for the year is based on the {{input.current_time}}")
        response: Optional[str] = Field(description="The final response to be displayed to the user. This can only be populated after the tool is called. The output of the tool goes here")

    If you are done say 'DONE' and return your new json with appropriate properties in the next line.
    If not, simply return the best properties you come up with.
    JSON:
    {# The following properties were not found in the json:
    {% for property in properties_to_validate %}
        {{property}}
    {% endfor %} #}
{% else%}
    Extract entities from the following context.

    Context: {{input}}
    Current Time: {{input.current_time}}
    Be sure to make your decisions considering that the current time and day is noted in the {{input.current_time}} value.
    The entities should be presented as key-value pairs in a JSON object.

    Example:
    {
        "input": {{input.user_input}},
        "output": {
            "name": "Winning Calendar event",
            "category": "always",
            "lead_time": 5,
            "event_time": "2024-05-05T10:30:00-04:00",
            "event_time_end": "2024-05-05T10:45:00-04:00",
            "location": "Court House",
            "error": false,
            "current_time": {{input.current_time}}
            }
    }

    Here is the schema for the JSON:
        name: str = Field(description="Name of the event")
        category: Category = Field(description="Category of the event")
        lead_time: int = Field(description="How long before the event I should be reminded. Defaults to 30 minutes if not provided.")
        event_time: datetime = Field(description="When the event should actually happen. Always following the 'America/New_York' timezone.")
        event_time_end: datetime = Field(description="When the event should actually end. Always following the 'America/New_York' timezone.")
        location: str = Field(description="Location of event, if provided")
        error: bool = Field(default=False, description="If there was an error in the input then True. Otherwise, False.")
        current_time: datetime = Field(description="The current time. Always following the 'America/New_York' timezone.")
        response: Optional[str] = Field(description="The final response to be displayed to the user. This can only be populated after the tool is called. The output of the tool goes here")
    
    If there are no possibilities for a particular category, return an empty list for this category.
    JSON:
{% endif %}
"""