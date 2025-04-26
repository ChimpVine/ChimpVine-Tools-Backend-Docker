import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Function to generate data options based on difficulty
def generate_data_options(difficulty,type):

    llm = get_llm()
    # Construct the file path for the correct prompt
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension','writing','data_table.txt')

    # Load the selected prompt template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt with the provided values
    
    
    formatted_prompt = prompt.replace("{difficulty}", difficulty).replace("{type}", (type))

    try:
        response = llm.predict(formatted_prompt)
        cleaned_response = response.replace("\n", " ").replace("\"", " ").replace("**", " ").replace("###", " ").strip()
        cleaned_response = cleaned_response.replace("  ", " ").replace("  ", " ").replace("```", " ").replace("json", " ").replace("\\n", " ").strip()
        

        try:
            parsed_output = json.loads(cleaned_response)
            return parsed_output
        except json.JSONDecodeError:
            # If not JSON, return the cleaned response directly
            return {"response": cleaned_response}
    except Exception as e:
        print(f"Error generating questions: {e}")
        return {"error": str(e)}
