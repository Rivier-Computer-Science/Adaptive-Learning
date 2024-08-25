# src/web_app.py

import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from src.data_collection import DataCollectionModule
from src.performance_dashboard import PerformanceDashboard

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
data_module = DataCollectionModule()
dashboard = PerformanceDashboard()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Ensure the uploads directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)
            process_file(file_path)
            return redirect(url_for('report'))
    return render_template('index.html')

def process_file(file_path):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        student_id = row['student_id']
        accuracy = row['accuracy']
        time_taken = row['time_taken']
        improvement = row['improvement']
        data_module.collect_data(student_id, accuracy, time_taken, improvement)
    dashboard.add_performance_data(data_module.get_reports())

@app.route('/report')
def report():
    img_base64 = dashboard.generate_visualizations()
    return render_template('report.html', img_data=img_base64)

if __name__ == '__main__':
    app.run(debug=True)
