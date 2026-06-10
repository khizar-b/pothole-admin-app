from flask import Blueprint, render_template, send_from_directory
import os

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    return render_template('login.html')

@pages_bp.route('/register')
def register():
    return render_template('register.html')

@pages_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@pages_bp.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

