# imports from flask
import json
import os
import ast
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urljoin, urlparse
from flask import abort, redirect, render_template, request, send_from_directory, url_for, jsonify  # import render_template from "public" flask libraries
from flask_login import current_user, login_user, logout_user, login_required
from flask.cli import AppGroup
from flask import current_app
# import "objects" from "this" project
from __init__ import app, db, login_manager  # Key Flask objects
# API endpoints
from api.user import user_api
from api.pfp import pfp_api
from api.review_api import review_api
from api.roads_api import roads_api
from api.upload_image import upload_api

from model.user import User, initUsers

# register URIs for api endpoints
app.register_blueprint(user_api)
app.register_blueprint(pfp_api)
app.register_blueprint(review_api) ## /api/review
app.register_blueprint(roads_api) ## /api/roads
app.register_blueprint(upload_api) ## /api/upload

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

custom_cli = AppGroup('custom', help='Custom commands')

@custom_cli.command('generate_data')
def generate_data():
    initUsers()

@app.route('/users/table')
@login_required
def utable():
    users = User.query.all()
    return render_template("utable.html", user_data=users)

@app.route('/users/table2')
@login_required
def u2table():
    users = User.query.all()
    return render_template("u2table.html", user_data=users)

login_manager.login_view = "login"

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.path))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_page = request.args.get('next', '') or request.form.get('next', '')
    if request.method == 'POST':
        user = User.query.filter_by(_uid=request.form['username']).first()
        if user and user.is_password(request.form['password']):
            login_user(user)
            if not is_safe_url(next_page):
                return abort(400)
            return redirect(next_page or url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template("login.html", error=error, next=next_page)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    print("Home:", current_user)
    return render_template("index.html")

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

custom_cli = AppGroup('custom', help='Custom commands')

@custom_cli.command('backup_data')
def backup_data():
    data = extract_data()
    save_data_to_json(data)
    backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'])

@custom_cli.command('restore_data')
def restore_data_command():
    data = load_data_from_json()
    restore_data(data)

app.cli.add_command(custom_cli)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8887")