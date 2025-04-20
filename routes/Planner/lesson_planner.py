from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from utils.Planner.Chat_with_lessonpanner import generate_lesson_plan
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
from validation.text_extraction import extract_text_from_pdf


lesson_planner_bp = Blueprint("lesson_planner", __name__)

UPLOAD_FOLDER = "/tmp"
tools = load_tools_from_json("Tools.json")


@lesson_planner_bp.route('/generate_lesson_plan', methods=['POST'])
def api_generate_lesson_plan():
    """API endpoint to generate a lesson plan."""
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')

        if not auth_token or not site_url:
            return jsonify({"error": "Missing headers"}), 400

        # Extract request data
        data = request.form or request.json
        file = request.files.get('file')
        lesson = data.get('command')
        grade = data.get('grade')
        duration = data.get('duration')
        subject = data.get('subject')

        # Validate required fields
        if not all([file, lesson, grade, duration, subject]):
            return jsonify({"error": "Missing required fields or file"}), 400

        # Validate lesson input
        valid, error = validate_string(lesson, "Lesson", 3, 500)
        if not valid:
            return jsonify({"error": error}), 400

        # Load and verify tool
        tool = get_tool_by_name(tools, "Lesson Planner")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID, Token = tool["Tool_ID"], tool["Token"]

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get("status") != "success":
            return jsonify({"error": token_verification.get("message")}), token_verification.get("code", 400)

        # Securely save the uploaded PDF
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(pdf_path)

        # Extract text from PDF
        pdf_text, error = extract_text_from_pdf(pdf_path)
        os.remove(pdf_path)

        if pdf_text is None:
            return jsonify({"error": error}), 500

        # Generate lesson plan
        command = f"Lesson: {lesson}\nGrade: {grade}\nDuration: {duration}\nSubject: {subject}"
        lesson_plan = generate_lesson_plan(pdf_text, command)
        
        # Parse string to dict if needed
        if isinstance(lesson_plan, str):
            lesson_plan = json.loads(lesson_plan)

        # Use token after successful response
        use_token(auth_token, site_url, Tool_ID, Token)

        return jsonify(lesson_plan), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
