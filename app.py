from flask import Flask, render_template, redirect, url_for, session
from cli_funcs import get_latest_version_cli, get_versions_cli, get_module_names_cli
from serve_files_cli import serve_latest_version, serve_specified_version
from database import db
from models import User, Module
from webui_funcs import login_webui, signup_user_webui, change_password_webui, main_page_webui, upload_modules_webui, delete_module_webui, update_module_webui, get_module_info_webui, get_profile_webui

# initializing and configuring the flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cul_db.db'
app.secret_key = "Atri Thakar"
db.init_app(app)

with app.app_context():
    db.create_all()

BASE_DIR = "c_cpp_modules"  # Directory containing all modules and versions

# for all the below routes, if you want to view the docstring, please refer to the respective function that is being called.
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def login():
    return login_webui()

@app.route('/signup',methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup',methods=['POST'])
def signup_user():
    return signup_user_webui()

@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/change_password',methods=['POST'])
def change_password():
    return change_password_webui()

@app.route('/profile',methods=['GET'])
def get_profile():
    return get_profile_webui()

@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    return main_page_webui()

@app.route('/upload_modules', methods=['GET','POST'])
def upload_modules():
    return upload_modules_webui()
    
@app.route('/delete_module/<module_id>', methods=['GET','POST'])
def delete_module(module_id):
    return delete_module_webui(module_id)

@app.route('/update_module/<module_id>', methods=['GET','POST'])
def update_module(module_id):
    return update_module_webui(module_id)

@app.route('/info/<module>/<version>')
def get_module_info(module, version):
    return get_module_info_webui(module, version)

@app.route('/files/<module_name>/<version>', methods=['GET'])
def serve_files(module_name, version):
    return serve_specified_version(module_name, version)

@app.route('/files/<module_name>/', methods=['GET'])
def serve_files_2(module_name):
    return serve_latest_version(module_name)

@app.route('/versions/<module_name>', methods=['GET'])
def get_versions(module_name):
    return get_versions_cli(module_name)

@app.route('/latest_version/<module_name>', methods=['GET'])
def get_latest_version(module_name):
    return get_latest_version_cli(module_name)

@app.route('/modules', methods=['GET'])
def get_module_names():
    return get_module_names_cli()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
