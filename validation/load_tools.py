import json
# Load tools from the JSON file
def load_tools_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        return []

# Function to get tool by name
def get_tool_by_name(tools, tool_name):
    # Use case-insensitive search and handle different key casings
    return next((tool for tool in tools if tool.get('tool_name', '').lower() == tool_name.lower() or 
                 tool.get('Tool_name', '').lower() == tool_name.lower()), None)
    