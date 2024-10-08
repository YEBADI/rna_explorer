from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import io
import uuid
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)

# Set secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Set the upload folder path
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Disable SQLAlchemy event notifications to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize the database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Define the Run model to track user uploads and results
class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    results_path = db.Column(db.String(150), nullable=False)
    plot_path = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Redirect root URL to the login page
@app.route('/')
def index():
    return redirect(url_for('login'))

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('login'))
    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('upload'))
        else:
            flash('Login failed. Check your username and/or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

# User logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# File upload route
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            return redirect(url_for('calculate_average', filename=unique_filename))
        else:
            flash('Invalid file type. Please upload a CSV file.')
            return redirect(url_for('upload'))
    return render_template('upload.html')

# Calculate and display results for the uploaded file
@app.route('/calculate/<filename>')
@login_required
def calculate_average(filename):
    # Check if the run already exists in the database
    run = Run.query.filter_by(user_id=current_user.id, filename=filename).first()
    if run:
        # If run exists, display the saved results and plot
        data = pd.read_csv(run.results_path).to_dict(orient='records')
        return render_template('result.html', data=data, image_url=url_for('static', filename=run.plot_path.split('/')[-1]), download_url=url_for('download_results', filename=run.results_path.split('/')[-1]))

    # If the run doesn't exist, process the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        flash('File not found. Please try uploading again.')
        return redirect(url_for('upload'))

    # Perform the calculations and generate the plot
    df = pd.read_csv(file_path, index_col=0)
    df2 = np.log2(df + 1)
    gene_means = df2.mean(axis=1)
    gene_means_df = gene_means.reset_index()
    gene_means_df.columns = ['Gene Symbol', 'Mean Log2 Gene Expression']

    data = gene_means_df.to_dict(orient='records')

    plot_filename = f"{uuid.uuid4()}_gene_distribution.png"
    plot_path = os.path.join('app', 'static', plot_filename)
    
    plt.figure(figsize=(30, 20))
    sns.histplot(gene_means, kde=True, bins=30)
    plt.title('Distribution of Avg Log 2 Gene Expression', fontsize=50)
    plt.xlabel('Avg Log 2 Gene Expression', fontsize=35)
    plt.ylabel('Log Frequency', fontsize=35)
    plt.yscale('log')
    
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    plt.savefig(plot_path, bbox_inches='tight') 
    plt.close()

    results_csv_filename = f"{uuid.uuid4()}_gene_expression_results.csv"
    results_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], results_csv_filename)
    gene_means_df.to_csv(results_csv_path, index=False)

    # Save the new run details in the database
    run = Run(user_id=current_user.id, filename=filename, results_path=results_csv_path, plot_path=plot_path)
    db.session.add(run)
    db.session.commit()

    return render_template('result.html', data=data, image_url=url_for('static', filename=plot_filename), download_url=url_for('download_results', filename=results_csv_filename))

# Route for downloading the results CSV
@app.route('/download/<filename>')
@login_required
def download_results(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('The requested file does not exist.')
        return redirect(url_for('upload'))

# Route to view previous runs by the logged-in user
@app.route('/previous_runs')
@login_required
def previous_runs():
    runs = Run.query.filter_by(user_id=current_user.id).order_by(Run.timestamp.desc()).all()
    return render_template('previous_runs.html', runs=runs)

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
