from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

users = {"oxygen": "pass123"}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('upload'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect(url_for('calculate_average', filename=file.filename))
    return render_template('upload.html')

@app.route('/calculate/<filename>')
def calculate_average(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file_path, index_col=0)
    df2 = np.log2(df + 0.00000000000000000000000001)
    gene_means = df2.mean(axis=1)
    return gene_means.to_frame(name = "Avg Log 2 Gene Expression").to_html()
    #plt.figure(figsize=(10, 6))
    #gene_means.plot(kind='bar')
    #plt.title('Average Gene Expression')
    #plt.ylabel('Expression Level')
    #plt.xlabel('Gene')
    #plt.savefig(os.path.join('static', 'gene_plot.png'))
    #plt.close()
    #return render_template('result.html', image_url=url_for('static', filename='gene_plot.png'))

if __name__ == '__main__':
    app.run(debug=True)
