from flask import request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
from models import User, Module
import os
import json
from rapidfuzz import process

BASE_DIR = "c_cpp_modules"

def login_webui():
    '''
    Returns the login page if the user is not logged in, else redirects to the main page

    Args:
        None

    Returns:
        login page: if the user is not logged in
        main page: if the user is logged in

    Raises:
        None
    '''
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return render_template('index.html', error="Invalid email or password")

    session['email'] = email
    return redirect(url_for('main_page'))

def signup_user_webui():
    '''
    Returns the signup page and adds the user to the database if the user does not exist. If the user already exists, returns an error message. After adding the user to the database, redirects to the login page.

    Args:
        None

    Returns:
        signup page: if the user requests for signup and incase of any error in the singup process
        login page: if the user is added successfully

    Raises:
        None
    '''
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    hashed_password = generate_password_hash(password)

    user = User(email=email, password=hashed_password, first_name=first_name, last_name=last_name, username=username)

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return render_template('signup.html', error="User already exists")
    
    user_name_exists = User.query.filter_by(username=username).first()
    if user_name_exists:
        return render_template('signup.html', error="Username already exists, pick a different username.")

    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

def change_password_webui():
    '''
    Changes the password of the user if the old password is correct. If the old password is incorrect, returns an error message.

    Args:
        None

    Returns:
        profile page: if the password is changed successfully
        profile page with error: if the old password is incorrect or any other error occurs

    Raises:
        None
    '''
    profile = User.query.filter_by(email=session.get('email')).first()
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    is_old_password_correct = check_password_hash(profile.password, old_password)
    if not is_old_password_correct:
        return render_template('profile.html', error="Old password is incorrect",profile=profile)
    User.query.filter_by(email=session.get('email')).update({'password': generate_password_hash(new_password)})
    db.session.commit()
    return render_template('profile.html', success="Password changed successfully", profile=profile)

def main_page_webui():
    '''
    Returns the main page if the user is logged in, else redirects to the index page

    Args:
        None

    Returns:
        main page: if the user is logged in
        login page: if the user is not logged in

    Raises:
        None
    '''
    if not session.get('email'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        module_name_input = request.form.get('module_name')
        
        # List all directories (module names) from BASE_DIR
        available_modules = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
        
        # Perform fuzzy search to get all matches
        all_matches = process.extract(module_name_input, available_modules, limit=None)
        
        # Filter matches with a similarity score above 70
        matched_modules = [match[0] for match in all_matches if match[1] > 70]
        
        module_versions_dict = {}  # Dictionary to store module names and their versions

        if matched_modules:
            error = None
            for module_name in matched_modules:
                versions_json = os.path.join(BASE_DIR, module_name, 'versions.json')
                if os.path.exists(versions_json):
                    with open(versions_json, 'r') as file:
                        module_versions = json.load(file)
                        module_versions_dict[module_name] = [item['version'] for item in module_versions.get('versions', [])]
                else:
                    error = "Some modules were found, but versions could not be loaded."

            return render_template('main_page.html', module_versions=module_versions_dict, error=error)
        else:
            error = "No matching modules found."
            return render_template('main_page.html', error=error)
    
    elif request.method == 'GET':
        return render_template('main_page.html')


def upload_modules_webui():
    '''
    If the request method is GET, returns the upload modules page. If the request method is POST, clones the module from the provided github link and adds the module to the database. If the module already exists, returns an error message. If the module is not found at the provided url, returns an error message. If the module is cloned successfully and added to the database, redirects to the main page. If any error occurs during the process, returns an error message.

    Args:
        None
    
    Returns:
        upload modules page: if the request method is GET
        main page: if the module is cloned successfully and added to the database
        upload modules page with error: if the module already exists or any error occurs during the process

    Raises:
        None
    '''
    if request.method == 'GET':
        return render_template('upload_modules.html')
    elif request.method == 'POST':
        module_url = request.form.get('github_repo_link')
        # assuming module_url is in the format: https://github.com/username/repo
        module_name = module_url.split('/')[-1]
        # check if the module already exists
        module = Module.query.filter_by(module_name=module_name).first()
        if module:
            return render_template('upload_modules.html', error="Module already exists")
        # check if module exists at provided url

        # clone the repo into the c_cpp_modules directory
        cloned_status = os.system(f"git clone {module_url} {os.path.join(BASE_DIR, module_name)}")
        if cloned_status != 0:
            return render_template('upload_modules.html', error="Error cloning the repository")
        module = Module(module_name=module_name, module_url=module_url, associated_user=session.get('email'))
        db.session.add(module)
        db.session.commit()
        return render_template('main_page.html')

def delete_module_webui(module_id):
    '''
    Deletes the module from the database and the c_cpp_modules directory. If the module is not found, returns an error message. If the module is deleted successfully, redirects to the profile page. If any error occurs during the process, returns an error message.

    Args:
        module_id: The id of the module to be deleted

    Returns:
        profile page: if the module is deleted successfully
        profile page with error: if the module is not found or any error occurs during the process

    Raises:
        None
    '''
    module = Module.query.filter_by(module_id=module_id).first()
    if not module:
        return render_template('profile.html', error="Module not found")
    os.system(f"rm -rf {os.path.join(BASE_DIR, module.module_name)}")
    db.session.delete(module)
    db.session.commit()
    profile = User.query.filter_by(email=session.get('email')).first()
    modules = Module.query.filter_by(associated_user=session.get('email')).all()
    return render_template('profile.html',profile=profile,modules=modules)

def update_module_webui(module_id):
    '''
    Updates the module by pulling the changes from the github repository. If the module is not found, returns an error message. If the module is updated successfully, redirects to the profile page. If any error occurs during the process, returns an error message.

    Args:
        module_id: The id of the module to be updated

    Returns:
        profile page: if the module is updated successfully
        profile page with error: if the module is not found or any error occurs during the process

    Raises:
        None
    '''
    module = Module.query.filter_by(module_id=module_id).first()
    if not module:
        return render_template('profile.html', error="Module not found")
    os.system(f"cd {os.path.join(BASE_DIR, module.module_name)} && git pull")
    profile = User.query.filter_by(email=session.get('email')).first()
    modules = Module.query.filter_by(associated_user=session.get('email')).all()
    return render_template('profile.html',profile=profile,modules=modules)

def get_module_info_webui(module, version):
    '''
    Queries the database to get the module information. If the module is not found, returns an error message. If the module is found, returns the module information. If the module has dependencies, returns the dependencies as well. If any error occurs during the process, returns an error message.

    Args:
        module: The name of the module
        version: The version of the module

    Returns:
        module information page: if the module is found
        error message: if the module is not found or any error occurs during the process

    Raises:
        None
    '''
    module_info_file_path = os.path.join(BASE_DIR, module, version, 'module_info.json')
    if not os.path.exists(module_info_file_path):
        return "<h1>Error 404: Module/Version not found.</h1>", 404
    module_info = None
    with open(module_info_file_path, 'r') as file:
        module_info = json.load(file)
    deps = module_info.get('requires', [])
    data = {
        "ModuleName": module,
        "Version": version,
        "Author": module_info.get('author'),
        "Description": module_info.get('description'),
        "License": module_info.get('license'),
        "Dependencies": {dep.split('==')[0]: dep.split('==')[1] for dep in deps} if deps else None,

    }
    # print(data)
    # print(jsonify(data))
    # return jsonify(data)
    return render_template('version_info.html', data=data)

def get_profile_webui():
    '''
    Returns the profile page if the user is logged in, else redirects to the index page

    Args:
        None

    Returns:
        profile page: if the user is logged in
        login page: if the user is not logged in

    Raises:
        None
    '''
    if session.get('email'):
        profile = User.query.filter_by(email=session.get('email')).first()
        return render_template('profile.html',profile=profile,modules=Module.query.filter_by(associated_user=session.get('email')).all())
    return redirect(url_for('index'))
