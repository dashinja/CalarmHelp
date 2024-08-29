google_calendar_feeder = """{% if properties_to_validate %}
    Here was the context you were provided:
    {{input.user_input}}

    Here are the entities you previously extracted:
    {%for property in properties_to_validate %}
    {{property}}
    {% endfor %}

    Are these the correct entities?
    Things to check for:
    - Entities can be only one of these: name, category, lead_time, event_time, event_time_end, location, error, current_time
    - Required entities are: name, category, lead_time, event_time, event_time_end, current_time
    - There should be no extra entities
    - There should be no missing entities
    - There should be no duplicate entities
    
    # Here is the schema for the JSON that you make must meet:
    # {
    #     name: str,
    #     category: Category,
    #     lead_time: int,
    #     event_time: datetime,
    #     event_time_end: datetime,
    #     location: str,
    #     error: bool,
    #     current_time: datetime,
    # }

    If you cannot find an event_time_end simply add 30 minutes to event_time.
    If not, simply return the best properties you come up with.
    If there are no possibilities for a particular entity, return an empty string.
    If you are done say 'DONE' and return the json on the next line.
    json output:
{% else%}
    Extract entities from the following context.

    Context: {{input.user_input}}
    Current Time: {{input.current_time}}
    Be sure to make your decisions considering that the current time and day is noted in the {{input.current_time}} value.
    The entities should be presented as key-value pairs in a JSON string.

    # Here is the schema for the JSON:
    # {
    #     name: str,
    #     category: Category,
    #     lead_time: int,
    #     event_time: datetime,
    #     event_time_end: datetime,
    #     location: str,
    #     error: bool,
    #     current_time: datetime,
    # }
    
    Example Input:
    {
    "input": "Fix your app at 2PM Today at home. Remind me 10 minutes beforehand."
    }
    
    Example Output:
    {
    "name": "Fix your app at home",
    "category": "home",
    "lead_time": 10,
    "event_time": "2024-08-25T14:00:00-04:00",
    "event_time_end": "2024-08-25T16:00:00-04:00",
    "location": "home",
    "error": false,
    "current_time": "2024-08-25T09:10:06.325722"
    }
    
    If there are no possibilities for a particular entity, return an empty string for this entity value.
    json output:
{% endif %}
"""

google_calendar_feeder2 = """{% if properties_to_validate %}
    Here was the context you were provided:
    {{input.user_input}}

    Here are the entities you previously extracted:
    {{properties_to_validate}}
    Are these the correct entities?
    Things to check for:
    - Entities should be exactly one of these: name, category, lead_time, event_time, event_time_end, location, error, current_time
    - Required entities are: name, category, lead_time, event_time, event_time_end, current_time
    - if entity 'category' is not provided, it should default to 'always'
    - Entity values should be in the correct format
    - There should be no extra entities
    - There should be no missing entities
    - There should be no duplicate entities
    
        Example Output:
    {
    "name": "Fix your app at home",
    "category": "home",
    "lead_time": 10,
    "event_time": "2024-08-25T14:00:00-04:00",
    "event_time_end": "2024-08-25T16:00:00-04:00",
    "location": "home",
    "error": false,
    "current_time": "2024-08-25T09:10:06.325722"
    }
    
    For 'event_time' and 'event_time_end' assume the day is the same as the current day unless otherwise noted.    
    If you cannot find an event_time_end simply add 30 minutes to event_time.
    If you are done say 'DONE' and return your new entities in the next line
    If not, simply return the best properties you come up with.
    If there are no possibilities for an optional entity, return an empty string.
    
    Do not explain yourself in the output.
    markdown json output:
{% else%}
    Extract entities from the following context.

    Context: {{input}}
    Current Time: {{input.current_time}}
    Be sure to make your decisions considering that the current time and day is noted in the {{input.current_time}} value.
    The entities should be presented as key-value pairs in a JSON string.

    Example Input:
    {
    "input": "Fix your app at 2PM Today at home. Remind me 10 minutes beforehand."
    }
    
    Example Output:
    {
    "name": "Fix your app at home",
    "category": "home",
    "lead_time": 10,
    "event_time": "2024-08-25T14:00:00-04:00",
    "event_time_end": "2024-08-25T16:00:00-04:00",
    "location": "home",
    "error": false,
    "current_time": "2024-08-25T09:10:06.325722"
    }

    Here is the schema for the JSON:
        name: str = Field(description="Name of the event")
        category: Category = Field(default=Category.ALWAYS, description="Category of the event")
        lead_time: int = Field(description="How long before the event I should be reminded. Defaults to 30 minutes if not provided.")
        event_time: datetime = Field(description="When the event should actually happen. Always following the 'America/New_York' timezone. Assume the day is the same as the current day unless otherwise noted.")
        event_time_end: datetime = Field(description="When the event should actually end. Always following the 'America/New_York' timezone. Assume the day is the same as the current day unless otherwise noted.")
        location: str = Field(description="Location of event, if provided")
        error: bool = Field(default=False, description="If there was an error in the input then True. Otherwise, False.")
        current_time: datetime = Field(description="The current time. Always following the 'America/New_York' timezone.")
    
    
    If you cannot find an event_time_end simply add 30 minutes to event_time.
    If there are no possibilities for an optional entity, return an empty string for this entity value.

    Do not explain yourself in the output.
    markdown json output:
{% endif %}
"""
