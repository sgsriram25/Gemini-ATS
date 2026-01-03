import os
from flask import Flask, request, render_template
from pypdf import PdfReader 
import json
from resumeparser import ats_extractor

app = Flask(__name__)
UPLOAD_PATH = "__DATA__"

if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    job_description = request.form.get('job_desc')
    doc = request.files.get('pdf_doc')
    
    if not doc or not job_description:
        return "Missing file or job description.", 400

    doc_path = os.path.join(UPLOAD_PATH, "temp_resume.pdf")
    doc.save(doc_path)
    
    # Extract text from PDF
    reader = PdfReader(doc_path)
    resume_text = "".join([page.extract_text() for page in reader.pages])

    # Call Gemini
    try:
        analysis_json = ats_extractor(resume_text, job_description)
        analysis_data = json.loads(analysis_json)
        return render_template('index.html', data=analysis_data)
    except Exception as e:
        return f"Error processing request: {str(e)}", 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)