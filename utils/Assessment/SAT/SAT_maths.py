import json
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from utils.Folder_config.file_handler import load_prompt_template
from utils.model.llm_config import get_llm
from validation.output_cleaning import clean_and_load_json

load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_math_quiz(topic, part1_qs, part2_qs, part3_qs, part4_qs, difficulty_level):

    llm = get_llm()

    # def load_prompt_template(file_path):
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             return file.read()
    #     except UnicodeDecodeError:
    #         try:
    #             with open(file_path, 'r', encoding='latin-1') as file:
    #                 return file.read()
    #         except Exception as e:
    #             return None
    #     except FileNotFoundError:
    #         return None
    #     except Exception as e:
    #         return None

    # Load the prompt template
    prompt_file_path = os.path.join('prompt_template', 'Assessment', 'SAT', 'SAT_maths.txt')  # Update this path to your file
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def generate_quiz_plan(topic, part1_qs, part2_qs, part3_qs, part4_qs, difficulty_level):
        # Create the prompt by inserting the parameters
        prompt = prompt_template.replace("{topic}", topic)\
                                .replace("{num_questions_part_1}", str(part1_qs))\
                                .replace("{num_questions_part_2}", str(part2_qs))\
                                .replace("{num_questions_part_3}", str(part3_qs))\
                                .replace("{num_questions_part_4}", str(part4_qs))\
                                .replace("{difficulty_level}", difficulty_level)

        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            return None

    # Generate the quiz
    output = generate_quiz_plan(topic, part1_qs, part2_qs, part3_qs, part4_qs, difficulty_level)

    if output is None:
        return "Error: Unable to generate math quiz."

    # # Clean up the output
    # output = output.replace("```", "").replace("json", "").strip()
    
    output=clean_and_load_json(output)
    
    # Remove sections with empty questions
    if "quiz" in output and "sections" in output["quiz"]:
        filtered_sections = [
            section for section in output["quiz"]["sections"]
            if section.get("questions")
        ]
        output["quiz"]["sections"] = filtered_sections

    return output

