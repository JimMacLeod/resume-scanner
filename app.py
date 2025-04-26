from flask import Flask, render_template, request, redirect, url_for
import os
from main import parse_resume

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return "No file part", 400
        file = request.files['resume']
        if file.filename == '':
            return "No selected file", 400
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            parsed_data = parse_resume(file_path)
            os.remove(file_path)  # clean up uploaded file
            if not parsed_data:
                return "Could not parse the uploaded resume.", 400
            return render_template('result.html', data=parsed_data)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)