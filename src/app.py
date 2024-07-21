from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from langchain_together import Together
from dotenv import load_dotenv
from llm.agent import ResumeAnalyzer
from utils.file_parser import load_file_from_path
import os
import re

try:
    load_dotenv()
except Exception:
    print("No .env file found")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['RESUME_UPLOAD_FOLDER'] = 'uploads/resume'
app.config['JOB_DESCRIPTION_UPLOAD_FOLDER'] = 'uploads/job_description'

ALLOWED_EXTENSIONS = {'pdf'}

llm = Together(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.0,
    max_tokens=1000
)

email_credentials = {
    "user": os.environ.get("EMAIL_USER"),
    "password": os.environ.get("EMAIL_PASSWORD")
}
Agent = ResumeAnalyzer(llm=llm, email_credentials=email_credentials)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.search(regex, email)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        resume_file = request.files.get('resume_file')
        job_description_file = request.files.get('job_description_file')
        resume_text = request.form.get('resume_text')
        job_description_text = request.form.get('job_description_text')

        if not email or not is_valid_email(email):
            return jsonify(message='Please provide a valid email address', status="error"), 400

        resume_path = None
        job_description_path = None

        if (resume_file or resume_text) and (job_description_file or job_description_text):
            if resume_file and allowed_file(resume_file.filename):
                resume_filename = secure_filename(resume_file.filename)
                resume_path = os.path.join(app.config['RESUME_UPLOAD_FOLDER'], resume_filename)
                resume_file.save(resume_path)
            elif resume_text:
                resume_path = os.path.join(app.config['RESUME_UPLOAD_FOLDER'], 'resume_text.txt')
                with open(resume_path, 'w') as f:
                    f.write(resume_text)

            if job_description_file and allowed_file(job_description_file.filename):
                job_description_filename = secure_filename(job_description_file.filename)
                job_description_path = os.path.join(app.config['JOB_DESCRIPTION_UPLOAD_FOLDER'], job_description_filename)
                job_description_file.save(job_description_path)
            elif job_description_text:
                job_description_path = os.path.join(app.config['JOB_DESCRIPTION_UPLOAD_FOLDER'], 'job_description_text.txt')
                with open(job_description_path, 'w') as f:
                    f.write(job_description_text)

            try:
                # Run the agent with the provided inputs
                resume = load_file_from_path(resume_path)
                job_description = load_file_from_path(job_description_path)
                result = Agent.create_and_send_report(resume=resume, job_description=job_description, email=email)
                
                if result["status"] == "Success":
                    return jsonify(message='Files successfully uploaded and report has been generated! Please check your email!', status="success")
                else:
                    return jsonify(message='An error occurred while trying to generate your report. Please try again later. We apologize for the inconvenience.', status="error"), 500

            except Exception as e:
                return jsonify(message=f'An unexpected error occurred: {str(e)}', status="error"), 500
        else:
            return jsonify(message='Please provide both a resume and a job description', status="error"), 400

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
