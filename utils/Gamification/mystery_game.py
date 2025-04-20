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

def generate_mysterycase(topic, difficulty, no_of_clues):

    llm = get_llm()

    # Load prompt template file
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'mystery_game.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return None  # Handle the error as needed

    # Replace placeholders in the prompt template
    prompt = prompt_template.replace("{case_study_topic}", topic)
    prompt = prompt.replace("{number_of_clues}", str(no_of_clues))
    prompt = prompt.replace("{difficulty_level}", difficulty)

    def generate_mystery_topic():
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating mystery case: {e}")
            return None

    # Logic for generating the mystery topic
    output = generate_mystery_topic()
    
    if output is None:
        return None  # Handle the error as needed

    output = clean_and_load_json(output)


    return output  