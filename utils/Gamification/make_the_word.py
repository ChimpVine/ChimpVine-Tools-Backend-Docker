import random
import json
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# def load_prompt_template(file_path):
#     """Load prompt template from a file."""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             return file.read()
#     except (UnicodeDecodeError, FileNotFoundError) as e:
#         print(f"Error loading file {file_path}: {e}")
#         return None

def shuffle_letters(letters):
    """Shuffle the given letters."""
    shuffled = letters[:]
    random.shuffle(shuffled)
    return shuffled

def generate_make_the_word(theme, difficulty_level, number_of_words):
    """Generate a word-building game based on theme, difficulty level, and number of words."""
    
    llm = get_llm(temp=1)
    
    
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'make_the_word.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    # Replace placeholders in the prompt
    prompt = prompt_template.replace("{theme}", theme) \
                            .replace("{difficulty_level}", difficulty_level) \
                            .replace("{number_of_words}", str(number_of_words))
    
    try:
        # Use the invoke method to get the response
        response = llm.invoke(prompt)

        # Ensure the response contains content
        if not response or not hasattr(response, 'content'):
            return "Error: Received an invalid response from the model."

        # Extract raw text from response
        response_text = response.content.strip()

        # Clean up formatting issues

        response_text = response_text.replace("```", "").replace("json", "").replace("\n", "").replace("\\", "")


    except Exception as e:
        return f"Error generating word-building game: {e}"
    
    # Ensure OpenAI output is properly formatted
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON response.\nRaw Output:\n{response_text}"

    # Process the generated words
    words_data = response_json.get('words', [])
    
    words_with_hints = []
    unique_letters = set()

    for word_info in words_data:
        word = word_info['word']
        hint = word_info['hint']
        words_with_hints.append({'word': word, 'hint': hint})  # Collect word and hint as a dict
        unique_letters.update(word)  # Add letters of each word

    # Add shuffled unique letters to the response JSON
    response_json['letters'] = shuffle_letters([letter.upper() for letter in unique_letters])
    response_json['words'] = words_with_hints 

    # Return final structured JSON
    return json.dumps(response_json, indent=2) 
