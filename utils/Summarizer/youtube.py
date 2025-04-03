from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import re, json
from flask import jsonify  # Use Flask's response formatting
from utils.model.llm_config import get_llm

from utils.Folder_config.file_handler import load_prompt_template  # Import the function
# Load environment variables from .env file
load_dotenv()

def YT_summary_generation(topic):
    llm = get_llm()  # Importing LLM from the external file
    
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path=""
    prompt_file_path = os.path.join('prompt_template', 'Summarizer', 'YT-summarizer.txt')
    print(prompt_file_path)
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

    # Clean up the lesson plan output
    output = output.replace("json", "").replace("```", "")
    # Convert the response to JSON format
    try:
        output_json = json.loads(output)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response received."}), 400

    # Check if the output contains an error message
    if "Error" in output_json and output_json["Error"] == "Invalid input provided. Please enter a valid transcript.":
        return jsonify({"error": "Invalid input provided. Please enter a valid transcript."}), 400

    return output

# def format_response_to_json(response_text):
#     json_output = {}
#     current_section = None
#     current_text = ""

#     # Regular expressions to identify headers and list items
#     header_pattern = re.compile(r"\*\*(.*?)\*\*")  # Matches headers enclosed in double asterisks
#     list_item_pattern = re.compile(r"^\* (.+)$", re.MULTILINE)  # Matches list items starting with a bullet point
    
#     # Split response text by lines to process each line
#     lines = response_text.splitlines()

#     for line in lines:
#         line = line.strip()  # Remove leading and trailing whitespace

#         # Check if the line is a header
#         header_match = header_pattern.match(line)
#         if header_match:
#             # Save previous section text before moving to a new section
#             if current_section:
#                 if current_text:
#                     json_output[current_section].append(current_text.strip())
#                 current_text = ""
            
#             current_section = header_match.group(1)
#             json_output[current_section] = []  # Initialize as a list for items in this section

#         elif current_section:
#             # Check if the line is a list item
#             list_item_match = list_item_pattern.match(line)
#             if list_item_match:
#                 # Save any accumulated text before adding list item
#                 if current_text:
#                     json_output[current_section].append(current_text.strip())
#                     current_text = ""
                
#                 json_output[current_section].append(list_item_match.group(1))
#             else:
#                 # Accumulate plain text lines
#                 current_text += f" {line}" if current_text else line

#     # Capture any remaining text after the last section
#     if current_section and current_text:
#         json_output[current_section].append(current_text.strip())

#     # Convert dictionary to a JSON string with indentation for readability
#     formatted_json = json.dumps(json_output, indent=4)
#     print("this:", formatted_json)
#     return formatted_json