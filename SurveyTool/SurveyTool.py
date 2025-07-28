from typing import Optional
from SurveyTool.CsvUtil import CsvUtil
from pathlib import Path
import pandas as pd
import csv

class SurveyTool():
    def __init__(
            self,
            survey_results: Path,
            survey_codebook: Path
    ):
        """Initialize a Survery Analyzer

        Args:
            survey_results (Path): path to survey results csv
            survey_codebook (Path): path to survery codebook
        """
        self.survey_results = survey_results
        self.survey_codebook = survey_codebook
        self.survey_codebook_csv = None
        self.survey_questions = None

        if not survey_results.exists():
            raise FileNotFoundError(f'{self,survey_results} not found')
        if not survey_results.suffix == '.csv':
            raise ValueError(f'{self.survey_results} must be a .csv file')
        if not survey_codebook.exists():
            raise FileNotFoundError(f'{self.survey_codebook} not found')
        if not survey_codebook.suffix == '.xlsx':
            raise ValueError(f'{self.survey_codebook} must be a .xlsx file')
        
    def codebook_to_csv(
            self
    ):
        """Converts xlsx into a plain CSV for better processing
        """
        codebook_df_dict = pd.read_excel(self.survey_codebook, sheet_name=None)
        codebook_df_dict['Codebook'].to_csv(self.survey_codebook.with_suffix('.csv'))
        self.survey_codebook_csv = CsvUtil(self.survey_codebook.with_suffix('.csv'))
        print(f'Succesfully wrote {self.survey_codebook.with_suffix('.csv')}')
    
    def question_lookup_dict(
            self,
            primary_header: str,
            excluded_variable_labels: Optional[list] = None
    ):
        survey_questions = {}
        if not excluded_variable_labels:
            excluded_variable_labels = []

        if self.survey_codebook_csv is None:
            self.codebook_to_csv()
            codebook_dict = self.survey_codebook_csv.to_dict()

        for row in codebook_dict:
            variable_label = row.get(primary_header, None)
            if not variable_label:
                raise KeyError(primary_header)
            if variable_label not in survey_questions and variable_label not in excluded_variable_labels:
                codes = {
                    "variable":row.get('Variable'),
                    "responses":{
                        str(row.get('Values')):row.get('Value_Labels')
                    }
                }
                survey_questions[variable_label] = codes
            elif variable_label in survey_questions and variable_label not in excluded_variable_labels:
                if (val := str(row.get('Values'))) not in survey_questions[variable_label]['responses']:
                    survey_questions[variable_label]['responses'][val] = row.get('Value_Labels')
        self.survey_questions = survey_questions
    
    def get_response(
            self,
            question: str
    ):
        """Get responses for a specific question
        
        Args:
            question (str): The question to get responses for
            
        Returns:
            pd.DataFrame: DataFrame containing question and responses
        """
        if not self.survey_questions:
            raise ValueError("Must call question_lookup_dict first")
            
        if question not in self.survey_questions:
            raise KeyError(f"Question '{question}' not found")
            
        response_rows = []
        with open(self.survey_results, 'r', newline='', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                var = self.survey_questions[question]['variable']
                response = row.get(var)
                if response:
                    res_row = {
                        "Question": question,
                        "Response": self.survey_questions[question]['responses'].get(response)
                    }
                    response_rows.append(res_row)
        return pd.DataFrame(response_rows)
    
    def vizualize_results(
            self,
            question: str
    ):
        import plotly.express as px

        response_df = self.get_response(question)
        response_counts = response_df['Response'].value_counts().reset_index()
        response_counts.columns = ['Response', 'Count']
        
        fig = px.pie(response_counts,
        names='Response',      # what labels each slice
        values='Count',        # size of each slice
        title=question,
        width=600,
        height=600)
        
        #fig.update_traces(textposition='outside')
        fig.update_layout(
            margin=dict(t=100),
            title_font_size=10,
            height=600,
            width=600
        )
        return fig










