import os
import json
import io
import zipfile
from flask import send_file, jsonify

BASE_DIR = "c_cpp_modules"

def serve_latest_version(module_name):
    '''
    Sends the latest version of the specified module as a zip file. If the module is not found, returns an error message. If the versions.json file is missing, returns an error message. If the latest module path is missing in the versions.json file, returns an error message. If the latest module path does not exist, returns an error message. If any error occurs during the process, returns an error message.

    Args:
        module_name: The name of the module
    
    Returns:
        zip file: if the latest version of the module is found
        error message: if the module is not found, the versions.json file is missing, the latest module path is missing in the versions.json file, the latest module path does not exist, or any error occurs during the process

    Raises:
        json.JSONDecodeError: If an error occurs while decoding the versions.json file
        Exception: If any other error occurs
    '''
    versions_file_path = os.path.join(BASE_DIR, module_name, 'versions.json')
    
    # Check if the module directory exists
    if not os.path.exists(os.path.join(BASE_DIR, module_name)):
        return jsonify({"error": f"Module '{module_name}' not found."}), 404

    # Check if the versions.json file exists
    if not os.path.exists(versions_file_path):
        return jsonify({"error": "The versions.json file is missing for the specified module."}), 404

    try:
        with open(versions_file_path, 'r') as file:
            data = json.load(file)
            latest_path = data.get('latest_path')
            version = data.get('latest')

            if latest_path:
                module_dir = os.path.join(BASE_DIR, latest_path)

                if not os.path.exists(module_dir):
                    return jsonify({"error": f"The latest module path '{latest_path}' does not exist."}), 404

                # Create an in-memory zip file
                zip_stream = io.BytesIO()
                with zipfile.ZipFile(zip_stream, 'w') as zipf:
                    for root, dirs, files in os.walk(module_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, module_dir))

                zip_stream.seek(0)  # Go back to the start of the stream
                return send_file(zip_stream, as_attachment=True, download_name=f"{module_name}_{version}.zip")
            else:
                return jsonify({"error": "The 'latest_path' key is missing in the versions.json file."}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500

def serve_specified_version(module_name, version):
    '''
    Sends the specified version of the specified module as a zip file. If the module is not found, returns an error message. If the specified version path does not exist, returns an error message. If any error occurs during the process, returns an error message.

    Args:
        module_name: The name of the module
        version: The version of the module

    Returns:
        zip file: if the specified version of the module is found
        error message: if the module is not found, the specified version path does not exist, or any error occurs during the process

    Raises:
        Exception: If any error occurs
    '''
    module_dir = os.path.join(BASE_DIR, module_name, version)
    module_dir_wo_version = os.path.join(BASE_DIR, module_name)
    # Check if the module directory exists
    if not os.path.exists(module_dir_wo_version):
        return jsonify({"error": f"Module '{module_name}' not found."}), 404
    if not os.path.exists(module_dir):
        return jsonify({"error": f"Module '{module_name}' with version {version} not found."}), 404

    try:
        # Create an in-memory zip file
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as zipf:
            for root, dirs, files in os.walk(module_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, module_dir))
        
        zip_stream.seek(0)  # Go back to the start of the stream
        return send_file(zip_stream, as_attachment=True, download_name=f"{module_name}_{version}.zip")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error occurred while serving files."}), 500