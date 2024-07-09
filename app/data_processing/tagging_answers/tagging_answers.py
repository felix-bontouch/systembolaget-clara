import pandas as pd
from dotenv import load_dotenv
import concurrent.futures

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from operator import itemgetter
from langchain.schema.runnable import RunnableMap

from . prompt_config import system_template

load_dotenv()

CHAT_MODEL = ChatOpenAI(temperature=0, model_name="gpt-4o")

def _set_up_tools(themes):
    
    # Function Description
    function_description = (
        "To identify the relevant themes present in the survey answer based on the survey description, "
        "the question asked to the respondent, and the themes included in the survey. This function also "
        "assesses the sentiment and urgency expressed by the respondent for each identified theme."
    )

    # Theme Items Schema
    theme_items = {
        "type": "object",
        "properties": {
            "theme": {
                "type": "string",
                "description": "The identified theme present in the survey answer.",
                "enum": [theme["theme_name"] for theme in themes]
            },
            "sentiment": {
                "type": "string",
                "description": "The overall sentiment expressed in the response about the specified theme.",
                "enum": ["positive", "negative", "neutral", "neither", "both"]
            },
            "urgency": {
                "type": "integer",
                "description": (
                    "A scale from 1-5 defining the overall urgency of this theme in the response. "
                    "A higher number indicates a stronger sense of urgency expressed by the respondent. "
                ),
                "enum": [1, 2, 3, 4, 5]
            }
        },
        "required": ["theme", "sentiment", "urgency"]
    }

    # Answer Theme Function Schema
    answer_theme_function = {
        "type": "function",
        "function": {
            "name": "answer_theme_identifier",
            "description": function_description,
            "parameters": {
                "type": "object",
                "properties": {
                    "themes": {
                        "type": "array",
                        "description": "List of relevant themes identified in the survey response.",
                        "items": theme_items
                    }
                },
                "required": ["themes"]
            }
        }
    }

    return answer_theme_function

def _set_up_chain(themes):
    prompt = ChatPromptTemplate.from_template(system_template)
    tool = _set_up_tools(themes)
    model = CHAT_MODEL.bind_tools([tool]) 
    chain = RunnableMap({
        "answer_id" : itemgetter("answer_id"),
        "data" : (
            {
                "answer": itemgetter("answer"), 
                "question": itemgetter("question"), 
                "themes": itemgetter("themes"), 
                "survey_description": itemgetter("survey_description")
                }
            | prompt
            | model
            | JsonOutputToolsParser()
        )
    })
    
    return chain

def process_llm_output(llm_output):

    preprocessed_data = pd.DataFrame()

    for i, item in enumerate(llm_output):

        temp = pd.DataFrame(item["data"][0]["args"]["themes"])
        temp["answer_id"] = item["answer_id"]

        preprocessed_data = pd.concat([preprocessed_data, temp])
        
    return preprocessed_data

def parse_answers(data, question, survey_description, themes, batch_size:int = 250):

    theme_list = ""
    
    for theme in themes[question]:
        if theme['theme_name'] != "General" : 
            theme_list += f"{theme['theme_name']} : {theme['theme_description']}\n"

    data = data.dropna(subset=question).copy()
    data["words"] = data[question].apply(lambda x:len(x.split(" ")))
    data = data[data["words"] > 3]
    
    chain = _set_up_chain(themes[question])
    
    # Send batch of answers at a time to LLM
    parsed_data = pd.DataFrame()
    for i in range(0, len(data), batch_size):
        # Batching
        temp = data.iloc[i:i+batch_size]
        batch = [
            {"answer": row[question], 
             "question": question, 
             "answer_id": idx, 
             "themes" : theme_list, 
             "survey_description": survey_description
             } for idx, row in temp.iterrows()]
        
        # Parse reviews with LLM
        llm_output = chain.batch(batch) 
        processed_output = process_llm_output(llm_output)
        parsed_data = pd.concat([parsed_data, processed_output])

    return parsed_data.reset_index(drop=True)