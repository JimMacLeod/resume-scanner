from flask import Flask, request, jsonify, render_template_string
from main import parse_resume, render_html_from_parsed_data
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

@app.route('/')
def home():
    return '''
        <h2>Upload your resume</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="resume">
            <br><br>
            <input type="submit" value="Parse Resume">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return "No file part", 400
    file = request.files['resume']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    parsed_data = parse_resume(path)
    if not parsed_data:
        return "Unable to parse file.", 500

    html_result = render_html_from_parsed_data(parsed_data)
    return render_template_string(f"""
        <h2>Resume Parsed Successfully</h2>
        {html_result}
        <br><a href="/">Upload another</a>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)