from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm
from validation.output_cleaning import clean_and_load_json

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def summary_generation(text, summary_format):

    llm = get_llm()
    
    # Debugging: check current directory
    # print("Current working directory:", os.getcwd())
    
    # def load_prompt_template(file_path):
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             return file.read()
    #     except UnicodeDecodeError:
    #         print(f"Unicode decoding error for file: {file_path}. Trying different encoding.")
    #         try:
    #             with open(file_path, 'r', encoding='latin-1') as file:
    #                 return file.read()
    #         except Exception as e:
    #             print(f"Error reading file {file_path}: {e}")
    #             return None
    #     except FileNotFoundError:
    #         print(f"File not found: {file_path}")
    #         return None
    #     except Exception as e:
    #         print(f"Unexpected error: {e}")
    #         return None

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path=""
    prompt_file_path = os.path.join('prompt_template', 'Summarizer', 'text_summarizer.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def generate_summary(text, summary_format):
        prompt = prompt_template.replace("{text}", text).replace("{summary_format}", summary_format)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_summary(text, summary_format)
    
    if output is None:
        return "Error: Unable to generate lesson plan."
    
    output=clean_and_load_json(output)
    
    return output


