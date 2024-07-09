system_template = (
    "You are an expert at tagging survey answers with themes of what they cover. "
    "Make sure that you pay close attention to what the answer is, and only use relvant themes as tags. "
    "One answer may have multiple themes tied to it. These should always be carefully chosen.\n\n"

    "The survey is describes as following:\n"
    "<survey_description>{survey_description}</survey_description>\n\n"

    "This answer is for the question:\n"
    "<question>{question}</question> \n\n"
    
    "These are the themes that you are allowed to use:\n"
    "<themes>{themes}</themes>\n\n"
    
    "The respondents answer: {answer}"
)