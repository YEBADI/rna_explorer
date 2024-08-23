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
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            unique_filename = f"{current_user.username}_{uuid.uuid4().hex}_{file.filename}"
            user_directory = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
            file_path = os.path.join(user_directory, unique_filename)
            file.save(file_path)
            return redirect(url_for('calculate_average', filename=unique_filename))
        else:
            flash('Invalid file type. Please upload a CSV file.')
            return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/calculate/<filename>')
@login_required
def calculate_average(filename):
    user_directory = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    file_path = os.path.join(user_directory, filename)
    df = pd.read_csv(file_path, index_col=0)  # Keep the gene symbols as the index
    df2 = np.log2(df + 1)
    gene_means = df2.mean(axis=1)
    gene_means_df = gene_means.reset_index()
    gene_means_df.columns = ['Gene Symbol', 'Mean Log2 Gene Expression']

    data = gene_means_df.to_dict(orient='records')

    plt.figure(figsize=(30, 20))
    sns.histplot(gene_means, kde=True, bins=30)
    plt.title('Distribution of Avg Log 2 Gene Expression', fontsize=50)
    plt.xlabel('Avg Log 2 Gene Expression', fontsize=35)
    plt.ylabel('Log Frequency', fontsize=35)
    plt.yscale('log')
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plot_path = os.path.join('app', 'static', 'gene_distribution.png')
    plt.savefig(plot_path, bbox_inches='tight') 
    plt.close()

    results_csv_path = os.path.join(user_directory, f'gene_expression_results_{uuid.uuid4().hex}.csv')
    gene_means_df.to_csv(results_csv_path, index=False)

    return render_template('result.html', data=data, image_url=url_for('static', filename='gene_distribution.png'))

@app.route('/download/<filename>')
@login_required
def download_results(filename):
    user_directory = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    file_path = os.path.join(user_directory, filename)
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
