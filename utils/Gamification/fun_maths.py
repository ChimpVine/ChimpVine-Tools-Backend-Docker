from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def math_problem_generation(grade_level, math_topic, interest):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )
    
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())
    
    def load_prompt_template(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            print(f"Unicode decoding error for file: {file_path}. Trying different encoding.")
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return None
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path=""
    
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'fun_maths.txt')
    print(prompt_file_path)
    prompt_template = load_prompt_template(prompt_file_path)
    print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def generate_math_problem(grade_level, math_topic, interest):
        prompt = prompt_template.replace("{grade_level}", str(grade_level))\
                        .replace("{math_topic}", str(math_topic))\
                        .replace("{interest}", str(interest))

        # prompt = prompt_template.replace("{grade_level}", grade_level).replace("{math_topic}", math_topic).replace("{interest}", interest)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating fun maths: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_math_problem(grade_level, math_topic, interest)
    
    if output is None:
        return "Error: Unable to generate fun maths."

    # Clean up the lesson plan output
    output = output.replace("```", "").replace("json", "").replace("\n", "")
    # print("Cleaned Output:", output)
    output_json = json.loads(output)
    return output_json