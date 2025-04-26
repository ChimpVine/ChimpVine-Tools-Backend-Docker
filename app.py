import os
import tempfile
from flask import Flask, request, jsonify, render_template
import requests
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import fitz  # PyMuPDF
import json
import time
import tiktoken
# from email_validator import validate_email, EmailNotValidError
import re

# Import Rubric Generation
from utils.Planner.rubric_generation import rubric_generation

# For Google Sheets update
from utils.Request_sheet import update_google_sheet

# For Wordpress Site 
import http.client
import json
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# Allow requests from any origin for the specified routes
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')


# # Ensure the temporary upload directory exists
# UPLOAD_FOLDER = tempfile.gettempdir()
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ===================== Assessment =====================
# Worksheet
from routes.Assessment.worksheet import worksheet_bp
app.register_blueprint(worksheet_bp)

# Workbook
from routes.Assessment.workbook import workbook_bp
app.register_blueprint(workbook_bp)

# Quiz
from routes.Assessment.quiz import quiz_bp
app.register_blueprint(quiz_bp)

# Group Work
from routes.Assessment.group_work import group_work_bp
app.register_blueprint(group_work_bp)

# SAT Maths
from routes.Assessment.SAT.SAT_maths import SAT_maths_bp
app.register_blueprint(SAT_maths_bp)

# Slide one
from routes.Assessment.slide_one import slide_one_bp
app.register_blueprint(slide_one_bp)

# Slide two
from routes.Assessment.slide_two import slide_two_bp
app.register_blueprint(slide_two_bp)


# ===================== Gamification =====================
# Word Puzzle
from routes.Gamification.word_puzzle import word_puzzle_bp
app.register_blueprint(word_puzzle_bp)

# Fun Maths
from routes.Gamification.fun_maths import fun_maths_bp
app.register_blueprint(fun_maths_bp)

# Make the Word
from routes.Gamification.make_the_word import make_the_word_bp
app.register_blueprint(make_the_word_bp)

# Teacher Joke
from routes.Gamification.teacher_joke import teacher_joke_bp
app.register_blueprint(teacher_joke_bp)

# Bingo
from routes.Gamification.bingo import bingo_bp
app.register_blueprint(bingo_bp)

# Mystery Game
from routes.Gamification.mystery_game import mystery_game_bp
app.register_blueprint(mystery_game_bp)

# Tongue Twisters
from routes.Gamification.tongue_twister import tongue_twisters_bp
app.register_blueprint(tongue_twisters_bp)


# ===================== Special Needs =====================
# Social Stories
from routes.Special_Needs.social_stories import social_stories_bp
app.register_blueprint(social_stories_bp)


# ===================== Summarizer =====================
# Text Summarizer
from routes.Summarizer.text_summarizer import text_summarizer_bp
app.register_blueprint(text_summarizer_bp)


from routes.Summarizer.youtube import YT_summary_bp
app.register_blueprint(YT_summary_bp)


# ===================== Learning =====================
# Vocabulary List
from routes.Learning.vocab import vocab_list_bp
app.register_blueprint(vocab_list_bp)


# ===================== Planner =====================
# Lesson Planner
from routes.Planner.lesson_planner import lesson_planner_bp
app.register_blueprint(lesson_planner_bp)

# SEL Planner
from routes.Planner.sel_planner import sel_plan_bp
app.register_blueprint(sel_plan_bp)


import json

# Load tools from the JSON file
# def load_tools_from_json(file_path):
#     try:
#         with open(file_path, 'r') as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print(f"Error: File '{file_path}' not found.")
#         return []
#     except json.JSONDecodeError:
#         print("Error: Failed to decode JSON.")
#         return []

# # Function to get tool by name
# def get_tool_by_name(tools, tool_name):
#     # Use case-insensitive search and handle different key casings
#     return next((tool for tool in tools if tool.get('tool_name', '').lower() == tool_name.lower() or 
#                  tool.get('Tool_name', '').lower() == tool_name.lower()), None)

# # Load tools from JSON file
# tools = load_tools_from_json('Tools.json')

# def extract_text_from_pdf(pdf_path):
#     # Open the PDF file and extract text
#     with fitz.open(pdf_path) as doc:
#         text = "".join(page.get_text() for page in doc)

#     # Use tiktoken to encode the text and get the token count
#     encoding = tiktoken.get_encoding("cl100k_base")  # Use the correct model encoding here
#     token_count = len(encoding.encode(text))
    
#     print("Extracted Text:", text)
#     print("Token Count:", token_count)

#     return text

def validate_string(input_value, field_name, min_length=1, max_length=None):
    if not isinstance(input_value, str):
        return False, f"{field_name} must be a string."
    
    input_value = input_value.strip()
    length = len(input_value)
    
    if length == 0:  # Explicitly handle empty values
        return False, f"{field_name} cannot be empty."

    if length < min_length:
        return False, f"{field_name} must be at least {min_length} characters long."
       
    if max_length and length > max_length:
        return False, f"{field_name} must be no longer than {max_length} characters."

    # Updated regex pattern to accept letters, digits, spaces, periods, comma and apostrophes
    pattern = r"^(?![\s.,']+$)[a-zA-Z0-9\s.,']+$"

    if not re.match(pattern, input_value):
        return False, f"{field_name} contains invalid characters."

    return True, None

@app.route('/generate-rubric', methods=['POST'])
def generate_rubric():
    # First check if the data is coming from a form or JSON
    if request.is_json:
        data = request.get_json()  # If the content is JSON, parse it
    else:
        data = request.form  # Otherwise, handle as form data

    # Access form or JSON fields
    grade_level = data.get('grade_level')
    assignment_description = data.get('assignment_description')
    
    # Use getlist() if it's form data; otherwise, access directly for JSON
    if isinstance(data, dict):  # If it's a dictionary (JSON)
        point_scale = data.get('point_scale')  # Get point_scale from JSON
    else:  # If it's form data (MultiDict)
        point_scale = data.getlist('point_scale')

    additional_requirements = data.get('additional_requirements')

    # Check if all required fields are present
    if not all([grade_level, assignment_description, point_scale, additional_requirements]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate 'Assignment Description' field
    valid, error = validate_string(assignment_description, "Assignment Description", min_length=3, max_length=500)
    if not valid:
        return jsonify({"error": error}), 400
    
    try:
        # Call your rubric generation function
        result = rubric_generation(grade_level, assignment_description, point_scale, additional_requirements)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

    
# For SAT english quiz
from utils.Assessment.SAT.SAT_english import generate_english_quiz

@app.route('/SAT_english', methods=['POST'])
def generate_english_quiz_route():
    data = request.json

    selected_types = data.get('selected_types', [])

    if not isinstance(selected_types, list) or not all(isinstance(t, str) for t in selected_types):
        return jsonify({"error": "selected_types must be a list of strings."}), 400

    valid_types = ["Passage Reading", "Data Interpretation", "Sentence Completion", "Writing & Language"]

    invalid_types = [t for t in selected_types if t not in valid_types]
    if invalid_types:
        return jsonify({"error": f"Invalid quiz types: {', '.join(invalid_types)}"}), 400

    quiz_data = generate_english_quiz(selected_types)

    return jsonify(quiz_data)
   

   
# Comprehension

# Import Comprehension Reading 
from utils.Assessment.Comprehension.reading.passage import generate_passage
from utils.Assessment.Comprehension.reading.question import generate_question

@app.route('/generate_passage', methods=['POST'])
def generate_passage_api():
    # Parse input JSON
    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty')
    no_of_words = data.get('no_of_words')

    valid_difficulties = ['easy', 'medium', 'hard']

    # Validate topic
    if not topic or not isinstance(topic, str):
        return jsonify({"error": "Topic must be a non-empty string."}), 400

    # Validate difficulty
    if difficulty not in valid_difficulties:
        return jsonify({
            "error": f"Invalid difficulty level: {difficulty}. Choose from {valid_difficulties}."
        }), 400

    # Validate and convert no_of_words
    try:
        no_of_words = int(no_of_words)  # Convert to int if possible
        if not (500 <= no_of_words <= 1000):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            "error": "Number of words must be an integer between 500 and 1000."
        }), 400

    # Generate the passage
    passage = generate_passage(
        topic=topic,
        difficulty=difficulty,
        no_of_words=no_of_words,
    )
    
    if passage is None:
        return jsonify({'error': 'Failed to generate passage'}), 500
    
    if 'error' in passage:
        return jsonify(passage), 400

    return jsonify({"passage": passage}), 200



   
@app.route('/generate_question', methods=['POST'])
def generate_question_api():
        # Parse input JSON
        data = request.json
        passage = data.get('passage')
        selected_questions = data.get('selected_questions')
        questions_per_type = data.get('questions_per_type')
        
        valid_question_types = ["True/False", "MCQs", "Fill in the Blanks", "Question/Answer"]

        if not isinstance(selected_questions, list) or not all(q in valid_question_types for q in selected_questions):
            return jsonify({
                "error": f"Invalid question type in {selected_questions}. Choose from {valid_question_types}."
            }), 400

        if not isinstance(questions_per_type, int) or questions_per_type not in [5, 10, 15]:
            return jsonify({
                "error": "Questions per type must be a positive integer and one of the following: 5, 10, or 15."
            }), 400

        # Generate the passage
        question = generate_question(
            passage=passage,
            selected_questions=selected_questions,
            questions_per_type=questions_per_type,
        )
        if question is None:
            return jsonify({'error': 'Failed to generate question'}), 500
        
        if 'error' in question:
            return jsonify(question), 400

        return question, 200
        

# Route for generating passage options
# Import Comprehension Reading 
from utils.Assessment.Comprehension.writing.writing import generate_writing_options
from utils.Assessment.Comprehension.writing.writingdata import generate_data_options

@app.route('/generate_writing', methods=['POST'])
def generate_writing():
        data = request.json
        topic = data.get('topic')
        difficulty = data.get('difficulty')
        type = data.get('type')

        # Validate inputs
        if not topic or not difficulty or not type:
            return jsonify({"error": "Missing required fields: 'topic', 'difficulty', or 'type'"}), 400
        
        question = generate_writing_options(topic, difficulty, type)
        if question is None:
            return jsonify({"status": "error", "message": "Failed to generate data"}), 500
        
        if 'error' in question:
            return jsonify(question), 400

        return jsonify(question),200


# Route for generating data options
@app.route('/generate_data', methods=['POST'])
def generate_data():
        data = request.json
        difficulty = data.get('difficulty')
        type = data.get('type')
        
        # Validate inputs
        if not difficulty or not type:
            return jsonify({"error": "Missing required fields: 'difficulty' or 'type'"}), 400
        
        data_response = generate_data_options(difficulty, type)
        if data_response is None:
            return jsonify({"status": "error", "message": "Failed to generate data"}), 500
        return jsonify(data_response),200
    

# New import for YT
# from utils.Summarizer.youtube import YT_summary_generation


# @app.route('/YT_summary', methods=['POST'])
# def get_response():
#     try:
#         # Get the topic input from the user
#         topic = request.json.get('topic', '').strip()

#         if not topic:
#             return jsonify({"error": "Video Transcript cannot be empty"}), 400

#         # Check if the topic consists of only symbols or spaces
#         if not re.search(r'[a-zA-Z]', topic):
#             return jsonify({"error": "Video Transcript cannot be pure symbols or spaces"}), 400
        
#         # Assuming YT_summary_generation is a function that processes the topic and returns the summary
#         response_text = YT_summary_generation(topic)
        
#         # Return the generated summary as JSON if no error is found
#         return response_text
    
#     except Exception as e:
#         # Handle any exceptions that occur during the process
#         print("Error occurred:", str(e))
#         return jsonify({"error": str(e)}), 500


# def api_request(auth_token, site_url, endpoint_suffix, Tool_ID,Token):
#     """
#     Helper function to perform API requests to the WordPress site.
#     """
#     # Parse the site URL
#     parsed_url = urlparse(site_url if site_url.startswith("http") else f"https://{site_url}")
#     domain, path = parsed_url.netloc, parsed_url.path.rstrip('/')

#     if not auth_token or not domain:
#         return {"status": "error", "message": "Authorization token and site URL are required"}
    
#     # Set headers and payload
#     headers = {
#         'Authorization': f"Bearer {auth_token}",
#         'Content-Type': 'application/json'
#     }
#     aitoolID = "1"
#     payload = json.dumps({
#         "AIToolID": Tool_ID,
#         'TokenUsed': Token
#     })

#     try:
#         # Create HTTPS connection and send request
#         conn = http.client.HTTPSConnection(domain)
#         endpoint = f"{path}/wp-json/teacher-tools/v1/{endpoint_suffix}"
#         conn.request("POST", endpoint, payload, headers)
        
#         response = conn.getresponse()
#         response_data = response.read().decode()
#         response_json = json.loads(response_data)
#         print(f"Response Status: {response.status}")
#         print(f"Response Data: {response_data}")
#         # Handle response based on status code
#         if response.status == 200 and response_json.get("success"):
#             return {"status": "success", "message": response_json.get("message")}
#         elif response.status in [400, 401, 403]:
#             return {
#                 "status": "error",
#                 "message": response_json.get("message", "Authentication or permission error"),
#                 "code": response.status
#             }
#         else:
#             return {"status": "error", "message": f"Unexpected Error. Status Code: {response.status}"}
#     except Exception as e:
#         print(f"Error calling WordPress API: {e}")
#         return {"status": "error", "message": "Failed to connect to WordPress API"}

# def verify_token(auth_token, site_url,Tool_ID,Token):
#     """
#     Function to verify the token using the WordPress API.
#     """
#     return api_request(auth_token, site_url, "check-token",Tool_ID,Token)

# def use_token(auth_token, site_url,Tool_ID,Token):
#     """
#     Function to use (subtract) the token using the WordPress API.
#     """
#     if not Token:
#         print("Error: TEST_TOKEN is not set in environment variables.")
#         return {"status": "error", "message": "Missing TEST_TOKEN"}
    
#     return api_request(auth_token, site_url, "use-token",Tool_ID,Token)    


if __name__ == '__main__':
    app.run(debug=True)
    
    
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8080)