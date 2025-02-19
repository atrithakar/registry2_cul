import os
import json
import io
from database import db
from models import Module
from flask import jsonify

BASE_DIR = "c_cpp_modules"

def get_latest_version_cli(module_name):
    '''
    Returns the latest version of the specified module. If the module is not found, returns an error message. If the versions.json file is missing, returns an error message. If any error occurs during the process, returns an error message.

    Args:
        module_name: The name of the module
    
    Returns:
        latest version: if the module is found and the versions.json file exists
        error message: if the module is not found, the versions.json file is missing, or any error occurs during the process

    Raises:
        json.JSONDecodeError: If an error occurs while decoding the versions.json file
        Exception: If any error occurs
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
            return jsonify({"latest": data.get('latest')})
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500

def get_versions_cli(module_name):
    '''
    Returns all the versions of the specified module. If the module is not found, returns an error message. If the versions.json file is missing, returns an error message. If any error occurs during the process, returns an error message.

    Args:
        module_name: The name of the module
    
    Returns:
        all versions: if the module is found and the versions.json file exists
        error message: if the module is not found, the versions.json file is missing, or any error occurs during the process

    Raises:
        json.JSONDecodeError: If an error occurs while decoding the versions.json file
        Exception: If any error occurs
    '''
    versions_file_path = os.path.join(BASE_DIR, module_name, 'versions.json')
    latest_version_path = None
    data = None
    module_info = None
    data_to_send = None
    
    # Check if the module directory exists
    if not os.path.exists(os.path.join(BASE_DIR, module_name)):
        return jsonify({"error": f"Module '{module_name}' not found."}), 404

    # Check if the versions.json file exists
    if not os.path.exists(versions_file_path):
        return jsonify({"error": "The versions.json file is missing for the specified module."}), 404

    try:
        with open(versions_file_path, 'r') as file:
            data = json.load(file)
            latest_version_path = os.path.join(BASE_DIR, data.get('latest_path'),'module_info.json')
            
        with open(latest_version_path, 'r') as file:
            module_info = json.load(file)

        data_to_send = {
            "all_versions": data,
            "author": module_info.get('author'),
            "description": module_info.get('description'),
            "license": module_info.get('license'),
        }
        return jsonify(data_to_send)
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500

def get_module_names_cli():
    """Fetch all module names from the 'module' table using SQLAlchemy."""
    try:
        modules = Module.query.all()  # Fetch all module records
        module_list = [m.module_name for m in modules]  # Convert to dicts
        return jsonify(module_list)  # Return as JSON
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database query failed"}), 500