# routes/Assessment/worksheet.py

from flask import Blueprint, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
import json
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
from validation.text_extraction import extract_text_from_pdf

# Import worksheet generation functions
from utils.Assessment.worksheet.mcq_single import generate_mcq_single
from utils.Assessment.worksheet.mcq_multiple import generate_mcq_multiple
from utils.Assessment.worksheet.tf_simple import generate_tf_simple
from utils.Assessment.worksheet.fib_single import generate_fib_single
from utils.Assessment.worksheet.fib_multiple import generate_fib_multiple
from utils.Assessment.worksheet.match_term_def import generate_match_term_def
from utils.Assessment.worksheet.short_answer_explain import generate_short_answer_explain
from utils.Assessment.worksheet.short_answer_list import generate_short_answer_list
from utils.Assessment.worksheet.long_answer import generate_long_answer
from utils.Assessment.worksheet.seq_events import generate_seq_events
from utils.Assessment.worksheet.ps_math import generate_ps_math

worksheet_bp = Blueprint("worksheet", __name__)

tools = load_tools_from_json("Tools.json")

@worksheet_bp.route('/generate', methods=['POST', 'GET'])
def generate():
    """API endpoint to generate various worksheet types."""
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')

        if not auth_token or not site_url:
            return jsonify({"error": "Missing headers"}), 400

        # Extract request data
        data = request.form or request.json
        file = request.files.get('pdf_file')

        subject = data.get('subject')
        grade = data.get('grade')
        number_of_questions = data.get('number')
        question_type = data.get('question-type')
        sub_question_type = data.get('sub-question-type')
        topic = data.get('textarea')

        # Validate required fields
        if not all([subject, grade, number_of_questions, question_type]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate topic
        valid, error = validate_string(topic, "Description", 3, 250)
        if not valid:
            return jsonify({"error": error}), 400

        # Process PDF if provided
        pdf_text = None
        if file:
            try:
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, secure_filename(file.filename))
                file.save(temp_path)
                pdf_text, error = extract_text_from_pdf(temp_path)
                os.remove(temp_path)
                
                if pdf_text is None:
                    return jsonify({"error": error}), 500
            except Exception as e:
                return jsonify({"error": f"Failed to process the uploaded file: {str(e)}"}), 500

        # Load and verify tool
        tool = get_tool_by_name(tools, "Worksheet")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID, Token = tool["Tool_ID"], tool["Token"]

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get("status") != "success":
            return jsonify({"error": token_verification.get("message")}), token_verification.get("code", 400)

        # Process based on question type
        if question_type == "MCQ" and sub_question_type == "MCQ_Single":
            response = generate_mcq_single(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "MCQ" and sub_question_type == "MCQ_Multiple":
            response = generate_mcq_multiple(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "TF_Simple":
            response = generate_tf_simple(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Single":
            response = generate_fib_single(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Multiple":
            response = generate_fib_multiple(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Match_Term_Def":
            response = generate_match_term_def(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Q&A" and sub_question_type == "Short_Answer_Explain":
            response = generate_short_answer_explain(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Q&A" and sub_question_type == "Short_Answer_List":
            response = generate_short_answer_list(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Q&A" and sub_question_type == "Long_Answer_Explain":
            response = generate_long_answer(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Sequencing":
            response = generate_seq_events(subject, grade, number_of_questions, topic, pdf_text)
        elif question_type == "Problem_Solving":
            response = generate_ps_math(subject, grade, number_of_questions, topic, pdf_text)
        else:
            return jsonify({"error": "Question type not supported"}), 400
        

        if isinstance(response, dict) and 'error' in response:
            return jsonify(response), 400
        
        # Ensure proper JSON format
        if isinstance(response, str):
            response = json.loads(response)

        # Use token after successful response
        use_token(auth_token, site_url, Tool_ID, Token)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500