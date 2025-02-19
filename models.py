'''
This file contains all the database model used in the application.
'''

from database import db

class User(db.Model):
    email = db.Column(db.String(80), primary_key = True)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=True)
    username = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"<email: {self.email}\npassword: {self.password}>"

class Module(db.Model):
    module_id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(80), nullable=False)
    module_url = db.Column(db.String(120), nullable=False)
    associated_user = db.Column(db.String(80), db.ForeignKey('user.email'), nullable=False)

    def __repr__(self):
        return f"<module_name: {self.module_name}\nmodule_url: {self.module_url}\nassociated_user: {self.associated_user}>"