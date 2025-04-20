from flask import Blueprint, request
from utils.Assessment.slide_two import second_slide
from validation.load_tools import load_tools_from_json

slide_two_bp = Blueprint("slide_two", __name__)

tools = load_tools_from_json("Tools.json")

@slide_two_bp.route('/slide_two', methods=['POST', 'GET'])
def slide_two_API():
    data = request.get_json() or request.form
    response_first_slide = data
    print(response_first_slide)

    response = second_slide(response_first_slide)
    return response
