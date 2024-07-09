import pandas as pd
import json

from .data_processing.tagging_answers.tagging_answers import parse_answers
from .data_processing.theme_generation.theme_generation import generate_theme_dict

def main():
    data = pd.read_excel("notebooks/data.xlsx")
    survey_description = "En enkät om användares åsikt kring en ny funktion i Systembolagets app där man kan beställa till butik."
    question_column = "Är det något du vill kommentera kring dina svar?"

    theme_dict = generate_theme_dict(data, survey_description, [question_column])
    with open('answer_theme_function.json', 'w') as json_file:
        json.dump(theme_dict, json_file, indent=4)

    parsed_data = parse_answers(data, question_column, survey_description, theme_dict)
    parsed_data.to_csv("parsed_answers.csv")

if __name__ == "__main__":
    main()
