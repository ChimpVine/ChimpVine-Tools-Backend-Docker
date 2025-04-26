from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import re, json
from flask import jsonify  # Use Flask's response formatting
from utils.model.llm_config import get_llm
from validation.output_cleaning import clean_and_load_json

from utils.Folder_config.file_handler import load_prompt_template  # Import the function
# Load environment variables from .env file
load_dotenv()

def YT_summary_generation(topic):
    llm = get_llm()  # Importing LLM from the external file
    
    # Debugging: check current directory
    # print("Current working directory:", os.getcwd())

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path=""
    prompt_file_path = os.path.join('prompt_template', 'Summarizer', 'YT-summarizer.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def generate_summary(topic):
        prompt = prompt_template.replace("{TOPIC}", topic)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_summary(topic)
    
    if output is None:
        return "Error: Unable to generate lesson plan."
    
    output=clean_and_load_json(output)

    # Check if the output contains an error message
    if "Error" in output and output["Error"] == "Invalid input provided. Please enter a valid transcript.":
        return jsonify({"error": "Invalid input provided. Please enter a valid transcript."}), 400

    return output