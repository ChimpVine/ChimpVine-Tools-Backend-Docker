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

def generate_group_work(subject, grade, topic, learning_objective, group_size):

    llm = get_llm()
    
    # Function to load and read prompt template
    # def load_prompt_template(file_path):
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             return file.read()
    #     except UnicodeDecodeError:
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

    # Path to the prompt template file in the 'prompt' folder
    prompt_file_path = os.path.join('prompt_template', 'Assessment', 'group_work.txt')
    prompt_template = load_prompt_template(prompt_file_path)
    
    if prompt_template is None:
        print("Failed to load prompt template.")
        return None

    # Replace placeholders in the prompt template with user inputs using str.replace()
    prompt = (
        prompt_template
        .replace("{Subject}", subject)
        .replace("{Grade_Level}", grade)
        .replace("{Topic}", topic)
        .replace("{Learning_Objective}", learning_objective)
        .replace("{Group_Size}", str(group_size))  # Convert group_size to string for replacement
    )


    # Generate the group work division
    try:
        response = llm.invoke(prompt)  # Changed to invoke
        if response is None:
            print("No response received from LLM.")
            return None
    except Exception as e:
        print(f"Error generating group work division: {e}")
        return None
    
    output=clean_and_load_json(output)

    return output

