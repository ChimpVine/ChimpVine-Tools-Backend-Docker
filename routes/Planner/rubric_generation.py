
# @app.route('/generate-rubric', methods=['POST'])
# def generate_rubric():
#     # First check if the data is coming from a form or JSON
#     if request.is_json:
#         data = request.get_json()  # If the content is JSON, parse it
#     else:
#         data = request.form  # Otherwise, handle as form data

#     # Access form or JSON fields
#     grade_level = data.get('grade_level')
#     assignment_description = data.get('assignment_description')
    
#     # Use getlist() if it's form data; otherwise, access directly for JSON
#     if isinstance(data, dict):  # If it's a dictionary (JSON)
#         point_scale = data.get('point_scale')  # Get point_scale from JSON
#     else:  # If it's form data (MultiDict)
#         point_scale = data.getlist('point_scale')

#     additional_requirements = data.get('additional_requirements')

#     # Check if all required fields are present
#     if not all([grade_level, assignment_description, point_scale, additional_requirements]):
#         return jsonify({"error": "Missing required fields"}), 400
    
#     # Validate 'Assignment Description' field
#     valid, error = validate_string(assignment_description, "Assignment Description", min_length=3, max_length=500)
#     if not valid:
#         return jsonify({"error": error}), 400
    
#     try:
#         # Call your rubric generation function
#         result = rubric_generation(grade_level, assignment_description, point_scale, additional_requirements)
        
#         if 'error' in result:
#             return jsonify(result), 400
        
#         return result
#     except Exception as e:
#         print(f"Error processing request: {e}")
#         return jsonify({"error": str(e)}), 500