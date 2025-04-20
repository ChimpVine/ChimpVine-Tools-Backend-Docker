import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize LLM once
llm = get_llm()

# Function to generate passage options based on initial inputs
def generate_question(passage, selected_questions, questions_per_type):
    # Construct the file path for the correct prompt
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension','reading','question.txt')

    # Load the selected prompt template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt with the provided values

    formatted_prompt = prompt.replace("{passage}", passage).replace("{selected_questions}", str(selected_questions)).replace("{questions_per_type}", str(questions_per_type))


    # Generate the passage using the LLM
    try:
        response = llm.predict(formatted_prompt)
        
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
    except Exception as e:
        return {"error": str(e)}




