import json
from flask import jsonify

def clean_and_load_json(output: str):
    """
    Cleans a string that might contain JSON wrapped in markdown/code blocks or other noise,
    and safely attempts to parse it into a Python dictionary.
    Returns a Flask response on error, or the cleaned JSON dict on success.
    """
    cleaned = output.replace("json", "").replace("```", "").replace("`", "").replace("\n", "")
    
    try:
        output_json = json.loads(cleaned)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response received."}), 400

    # Handle known model-generated errors
    if isinstance(output_json, dict) and "Error" in output_json:
        return jsonify({"error": output_json["Error"]}), 400

    return output_json  # Success case
