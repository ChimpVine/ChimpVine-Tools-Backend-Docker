def load_prompt_template(file_path):
    """
    Load a prompt template from a given file path.

    :param file_path: str - Path to the prompt template file
    :return: str or None - Returns file content or None if an error occurs
    """
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
