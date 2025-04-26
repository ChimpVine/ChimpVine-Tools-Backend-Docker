import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm
from validation.output_cleaning import clean_and_load_json


# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_joke(topic, number_of_jokes):
    
    llm = get_llm()
    
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())

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

    # Adjust the relative path to point directly to the joke prompt template file
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'teacher_joke.txt')

    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return None  # Handle the error as needed


    def generate_joke_topic(topic, number_of_jokes):
        # Ensure number_of_jokes is a string for prompt replacement
        prompt = prompt_template.replace("{topic}", topic).replace("{number_of_jokes}", str(number_of_jokes))
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating joke: {e}")
            return None

    # Logic for generating jokes
    output = generate_joke_topic(topic, number_of_jokes)
    
    if output is None:
        return None  # Handle the error as needed
        
    output = clean_and_load_json(output)

    
    return output