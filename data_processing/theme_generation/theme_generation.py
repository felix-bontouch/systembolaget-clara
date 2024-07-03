import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv
import concurrent.futures

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_tools import JsonOutputToolsParser

from .prompt_config import survey_function, batch_template, summary_template

load_dotenv()

CHAT_MODEL = ChatOpenAI(
    temperature=0, 
    model_name="gpt-4o"
    )

def _set_up_templates():
    batch_prompt = ChatPromptTemplate.from_template(batch_template)
    summary_prompt = ChatPromptTemplate.from_template(summary_template)
    
    return batch_prompt, summary_prompt

def _set_up_chains(batch_prompt, summary_prompt):
    
    model = CHAT_MODEL.bind_tools([survey_function]) 
    batch_chain = batch_prompt | model | JsonOutputToolsParser() 
    summary_chain = summary_prompt | model | JsonOutputToolsParser()

    return batch_chain, summary_chain

def get_batch_answers(data, survey_description, question_column):

    batch = []
    batch_size = 250
    data = data[~data[question_column].isna()]

    for i in range(0, len(data), batch_size):
        temp = data.iloc[i:i+batch_size]
        answers = "\n\n".join(temp[question_column])
        batch.append({
            "question": question_column, 
            "answers" : answers, 
            "survey_description" : survey_description
            })
        
    return batch

def get_string_summary(responses):
    
    collection = ""
    
    for run, response in enumerate(responses):
        collection+=f"# SUMMARY {run+1}:\n"
        for theme in response[0]["args"]["major_themes"]:
            theme_summary = (
                f"<theme_name>{theme['theme_name']}</theme_name>\n"
                f"<theme_description>{theme['theme_description']}</theme_description>\n"
                f"<information>Sentiment:{theme['sentiment']}\nFrequency: {theme['frequency']}/5\n"
                "Urgency: {theme['urgency']}/5</information>\n"
                "---\n"
            )
            collection+=f"{theme_summary}"
        
    return collection

def get_question_summary(data, survey_description,  question):
    
    batch_prompt, summary_prompt = _set_up_templates()
    batch_chain, summary_chain = _set_up_chains(batch_prompt, summary_prompt)
    
    data = data.dropna(subset=question)
    data["words"] = data[question].apply(lambda x:len(x.split(" ")))
    data = data[data["words"] > 3].copy()
    
    batch = get_batch_answers(data, survey_description, question)
    responses = batch_chain.batch(batch)    
    string_summary = get_string_summary(responses)
    
    question_summary = summary_chain.invoke({
        "answer_summary" : string_summary, 
        "survey_description": survey_description, 
        "question" : question
        })
    
    return question_summary[0]["args"]["major_themes"]

def generate_theme_dict(data, survey_description, questions):
    theme_dict = {}

    # Using ThreadPoolExecutor to process each question in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a future for each question
        futures = {executor.submit(get_question_summary, data, survey_description, question): question for question in questions}

        # As each future completes, update theme_dict
        for future in concurrent.futures.as_completed(futures):
            question = futures[future]
            try:
                question_summary = future.result()
                theme_dict[question] = question_summary
            except Exception as exc:
                print(f'{question} generated an exception: {exc}')

    return theme_dict