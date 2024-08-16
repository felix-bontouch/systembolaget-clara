import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, settings):
        self.conn = psycopg2.connect(
            host=settings.db_host,
            database=settings.db_name,
            user=settings.db_username,
            password=settings.db_password,
            port=settings.db_port,
            cursor_factory=RealDictCursor
        )
        self.cursor = self.conn.cursor()

    def _get_dataframe(self, cursor) -> pd.DataFrame:
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)

    def fetch_survey_by_id(self, survey_id) -> pd.DataFrame:
        query = 'SELECT * FROM surveys WHERE "SurveyID" = %s'
        self.cursor.execute(query, (survey_id,))
        return self._get_dataframe(self.cursor)
    
    def fetch_answers_with_questions(self) -> pd.DataFrame:
        query = '''
        SELECT 
            a."AnswerID",
            a."SurveyID",
            a."QuestionID",
            a."ResponseID",
            a."NumericalResponse",
            a."StringResponse",
            q."QuestionText",
            q."QuestionType",
            q."QuestionSubjectText",
            s."SubjectID"
        FROM answers a
        JOIN questions q ON a."QuestionID" = q."QuestionID"
        JOIN subjects s ON q."QuestionSubjectText" = s."QuestionSubjectText"
        '''
        self.cursor.execute(query)
        return self._get_dataframe(self.cursor)
    
    def fetch_survey_description(self, survey_name) -> str: 
        query = 'SELECT "SurveyDescription" FROM surveys WHERE "SurveyName" = %s'
        self.cursor.execute(query, (survey_name,))
        survey_description = [desc["SurveyDescription"] for desc in self.cursor.fetchall()]
        return survey_description[0]

    def fetch_questions_by_survey_id(self, survey_id) -> pd.DataFrame:
        query = 'SELECT * FROM questions WHERE "SurveyID" = %s'
        self.cursor.execute(query, (survey_id,))
        return self._get_dataframe(self.cursor)
    
    def save_summaries_to_insights(self, summaries: pd.DataFrame) -> None:
        insert_query = '''
        INSERT INTO insights ("SubjectID", "InsightID", "InsightName", "InsightDescription")
        VALUES (%s, %s, %s, %s)
        ON CONFLICT ("InsightID") 
        DO UPDATE SET 
            "SubjectID" = EXCLUDED."SubjectID",
            "InsightName" = EXCLUDED."InsightName",
            "InsightDescription" = EXCLUDED."InsightDescription";
        '''
        for _, row in summaries.iterrows():
            self.cursor.execute(
                query=insert_query, 
                vars=(row['SubjectID'], row['InsightID'], row['InsightName'], row['InsightDescription'])
                )
        self.conn.commit()

    def fetch_survey_summaries(self):
        query = 'SELECT * FROM insights'
        self.cursor.execute(query)
        return self._get_dataframe(self.cursor)

    def close(self):
        self.cursor.close()
        self.conn.close()
