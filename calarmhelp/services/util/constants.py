Examples = [ 
            {
                "input": {
                "user_input": "Test CalendarAPI Setup at 3:30pm today at home for 10 minutes. Tell me 13 minutes before.",
                "current_time": "2024-05-04T14:27:50.983855"
                }, 
                "output": {
                "json": {
                    "name": "Test CalendarAPI Setup",
                    "category": "home",
                    "lead_time": 13,
                    "event_time": "2024-05-04T15:30:00-04:00",
                    "event_time_end": "2024-05-04T15:40:00-04:00",
                    "location": "home",
                    "error": False,
                    "current_time": "2024-05-04T14:27:50.983855"
                    },
                    "response": "Test CalendarAPI Setup @ 03:30 PM at home on Saturday May 04 #home [13m]"
                }
            },
            {
                "input": {
                    "user_input": "Winning Calendar event at 10.30AM tomorrow for 15 minutes. 5 minute headsup.",
                    "current_time": "2024-05-04T00:17:08.195955"
                },
                "output": {
                    "json": {
                        "name": "Winning Calendar event",
                        "category": "always",
                        "lead_time": 5,
                        "event_time": "2024-05-05T10:30:00-04:00",
                        "event_time_end": "2024-05-05T10:45:00-04:00",
                        "location": "",
                        "error": False,
                        "current_time": "2024-05-04T00:17:08.195955"
                    },
                    "response": "Winning Calendar event @ 10:30 AM on Sunday May 05 #always [5m]"
                },
            },
            {
                "input": {
                    "user_input": "Winning Calendar event at 10.30AM for 15 minutes. 53 minute headsup. It will be at Disney World.",
                    "current_time": "2024-05-04T00:16:05.482223"
                },
                "output": {
                    "json": {
                        "name": "Winning Calendar event",
                        "category": "always",
                        "lead_time": 53,
                        "event_time": "2024-05-04T10:30:00-04:00",
                        "event_time_end": "2024-05-04T10:45:00-04:00",
                        "location": "Disney World",
                        "error": False,
                        "current_time": "2024-05-04T00:16:05.482223"
                    },
                    "response": "Winning Calendar event @ 10:30 AM on Saturday May 04 #always [5m]"
                },
            }
        ]


CalarmHelpPromptTemplate = """
        Given the event details described in `{user_input}` and considering the current time is `{current_time}`, create a structured Python dictionary that represents these details, ensuring the event is scheduled for the future relative to `{current_time}`. 
        
        The output should be a Python dictionary named `event_details`, which includes the event's name, category, lead time, start and end times (in 'America/New_York' timezone), location (if applicable), and an error flag (set to True if the event is incorrectly specified, such as being scheduled in the past).

        Category can only be one of these: "always", "work", "home". If the category is unclear, default to "always".

        "current_time" is a required parameter. It is the current time in 'America/New_York' timezone.

        If the prompt does not specify whether the event is for today, tomorrow, or a future date, assume it is for today.

        If the time specified has already passed, assume it is for the next occurrence of that time - i.e. the next day.
        
        Here is the current user_input and current_time:
        {user_input}
        {current_time}

        Finally, run the output through the tool attached to the agent to get the final response in a field called response. ALWAYS use the tool.

        Return a json object that has a field for the final response, as well as a field for the json.
        
        Do not respond with any explanations or other information. Just the json object."""
