import os
import json
# from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize LLM once
llm = get_llm()

# Function to generate passage options based on initial inputs
def generate_passage(topic, difficulty, no_of_words):

    # Construct the file path for the prompt template
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension', 'reading','passage.txt')

    # Load the template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt
    formatted_prompt = prompt.replace("{difficulty}", difficulty).replace("{topic}", topic).replace("{no_of_words}", str(no_of_words))

    # Generate the passage using the LLM
    try:
        response = llm.predict(formatted_prompt)

        # Clean up response if needed (minimal modifications)
        cleaned_response = response.strip()

        # Attempt to parse as JSON
        try:
            parsed_output = json.loads(cleaned_response)
            # Format the parsed output as a JSON string
            return json.dumps(parsed_output, indent=4)
        except json.JSONDecodeError:
            # If not JSON, return the cleaned response directly as a JSON string
            return json.dumps({"response": cleaned_response}, indent=4)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return json.dumps({"error": str(e)}, indent=4)

