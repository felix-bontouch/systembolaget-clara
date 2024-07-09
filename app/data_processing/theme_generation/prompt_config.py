batch_template = (
    "You are set to analyze the responses for a survey that is described as this:\n"
    "<survey_description>{survey_description}</survey_description>\n\n"

    "The following content is a set of survey answers for the question:"
    "<question>{question}</question>\n\n"

    "Answers:\n"
    "<answers>{answers}</answers>\n\n"

    "Instructions:\n"
    "Based on this list, please identify the main themes.\n"
    "The themes should be in a list. Every theme should have a short name and a well "
    "written description of user opinions.\n"
    "Pay close attention to the frequency and urgency of the answers.\n"
    "Include only insights that are prevalent in multiple answers and can be used to "
    "describe more general opinions.\n"
    "Always use the survey_theme_identifier function."
)

summary_template = (
    "You are set to analyze the responses for a survey that is described as this:\n"
    "<survey_description>{survey_description}</survey_description>\n\n"
    
    "The following is set of summaries of main themes for the question: "
    "<question>{question}</question> in the survey:\n"
    
    "<answer_summar>{answer_summary}</answer_summar>\n\n"
    
    "Instructions:"
    "Take these and distill it into a final, consolidated summary of the main themes.\n"
    "Make sure to make the list as relevant and consice as possible.\n"
    "Make sure that similar themes are consolidated into one.\n"
    "Every theme should have a name and a well written section on the details of the repondents opinions.\n"
    "Include only insights that can be used to describe more general opinions.\n"
    "The themes should be in a list in plain string format.\n"
    "Always include a theme called General, with an overall summary of the opinions.\n"
    "Always use the survey_theme_identifier function."
)

function_description = (
    "To identify the main themes present in the survey answers, based on the survey descirption "
    "and the question that has been asked to the respondent. Close attention must be paid the the "
    "frequency and urgency and the responses."
)

major_themes_items = {
    "type" : "object",
    "properties" : {
        "theme_name" : {
            "type" : "string",
            "description" : "A descriptive name for the identified theme in Swedish"
        },
        "theme_description" : {
            "type" : "string",
            "description" : "A longer description in Swedish that captures the overall opinion and variance of the identified theme."
        },
        "sentiment" : {
            "type" : "string",
            "description" : "What the overall sentiment is in the responses about the specified theme.",
            "enum" : ["positive", "negative", "neutral", "neither"]
        },
        "frequency" : {
            "type" : "integer",
            "description" : "A scale from 1-5 defining the overall frequency of this theme. A higher number means higher frequency. 5 indicates a very high frequency among responents.",
            "enum" : [1,2,3,4,5]
        },
        "urgency" : {
            "type" : "integer",
            "description" : "A scale from 1-5 defining the overall urgency of this theme. A higher number means higher urgency for the respondents. 5 indicates a very high urgency among responents.",
            "enum" : [1,2,3,4,5]
        }
    },
     "required": ["theme_name", "theme_description", "sentiment", "frequency", "urgency"]
}

survey_function = {
    "type": "function",
    "function": {
        "name": "survey_theme_identifier",
        "description": function_description,
        "parameters": {
            "type": "object",
            "properties": {
                "major_themes": {
                    "type": "array",
                    "description": "List of distinct main themes in the survey responses.",
                    "items" : major_themes_items
                }
            },
            "required": ["major_themes"]
        }
    }
}