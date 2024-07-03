import pandas as pd
from dotenv import load_dotenv
import concurrent.futures

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from operator import itemgetter
from langchain.schema.runnable import RunnableMap

load_dotenv()

def set_up_chain():
    
    system_prompt = """
    You are an expert at tagging survey answers with themes of what they cover.
    Make sure that you pay close attention to what the answer is, and only use relvant themes as tags.

    The survey is describes as following:
    {survey_description}

    This answer is for the question: 
    {question}

    The output provided should follow this JSON format exactly, with the keys 'answer' and 'theme'.
    """

    system_prompt += "\n{{'answer' : [{{'theme':}},{{'theme':}}]}}"

    messages = [
        ("system", system_prompt),
        ("user", "Tag the survey answer below into the following themes: {themes}:" + "\n\nAnswer: '{answer}'"),
        ("user", "Complete and correct JSON structure with keys 'answer' and 'theme'")
    ]

    prompt = ChatPromptTemplate.from_messages(messages)
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
            | ChatOpenAI(
                model="gpt-3.5-turbo-0125", 
                temperature=0.1,
                model_kwargs={"response_format": { "type": "json_object" }}
            )
        )
    })
    
    return chain

def process_llm_output(llm_output):

    preprocessed_data = pd.DataFrame()

    for i, item in enumerate(llm_output):

        try:
            temp = pd.json_normalize(eval(item["data"].content)["answer"])
        except:
            string_json = item["data"].content.strip("`").replace("json","")
            temp = pd.json_normalize(eval(string_json)["answer"])
        temp["answer_id"] = item["answer_id"]

        preprocessed_data = pd.concat([preprocessed_data, temp])
        
    return preprocessed_data
    
def parse_answers(data, question, survey_description, themes, batch_size:int = 250):

    theme_list = ""
    
    for theme, description in themes[question].items():
        if theme != "General" : 
            theme_list += f"{theme} : {description}\n"

    data = data.dropna(subset=question).copy()
    data["words"] = data[question].apply(lambda x:len(x.split(" ")))
    data = data[data["words"] > 3]
    
    chain = set_up_chain()
    
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
        llm_output = process_llm_output(llm_output)
        llm_output["question"] = question

        # Join data into one large dataframe
        parsed_data = pd.concat([parsed_data, llm_output])
        parsed_data = parsed_data.reset_index(drop=True)

    return parsed_data

def process_question(question, data, survey_description, themes, batch_size=250):
    parsed_data = parse_answers(
        data=data, 
        question=question, 
        survey_description=survey_description,
        themes=themes,
        batch_size=batch_size
        )
    return question, parsed_data


def get_parsed_df(data, survey_description, theme_dict):
    parsed_df = pd.DataFrame()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a future for each question
        futures = {executor.submit(
            process_question, 
            question, 
            data, 
            survey_description, 
            theme_dict
            ): question for question in theme_dict.keys()}

        # As each future completes, process and store the result
        for future in concurrent.futures.as_completed(futures):
            question = futures[future]
            try:
                question, parsed_data = future.result()
                merged_df = parsed_data.merge(data[question], left_on="answer_id", right_index=True, how="left")
                merged_df = merged_df.rename(columns={question: "answer"})
                parsed_df = pd.concat([parsed_df, merged_df])
            except Exception as exc:
                print(f'{question} generated an exception: {exc}')
    
    return parsed_df