from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def sel_generation(grade, sel_topic, learning_objectives, duration):
    
    llm = get_llm()
        
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
    prompt_file_path = os.path.join('prompt_template','Planner', 'sel_planner.txt')
    prompt_template = load_prompt_template(prompt_file_path)


    if prompt_template is None:
        return "Error: Unable to load prompt template."
        
    def generate_sel(grade, sel_topic, learning_objectives, duration):

        # Create the prompt using the string versions
        prompt = (
            prompt_template.replace("{grade}", str(grade))
            .replace("{SEL_TOPIC}", sel_topic)
            .replace("{Learning_Objective}", str(learning_objectives))  # Use the converted string here
            .replace("{duration}", duration)
        )
        
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_sel(grade, sel_topic, learning_objectives, duration)
    
    if output is None:
        return "Error: Unable to generate lesson plan."

    # Clean up the lesson plan output
    output = output.replace("json", "")
    output = output.replace("```", "")
    
    output = json.loads(output)    
    return output

