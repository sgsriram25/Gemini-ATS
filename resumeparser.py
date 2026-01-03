from google import genai
from google.genai import types
import yaml
import json

def get_config():
    with open("config.yaml") as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def ats_extractor(resume_text, job_description):
    config = get_config()
    client = genai.Client(api_key=config['GEMINI_API_KEY'])

    prompt = f"""
    You are an expert Technical Recruiter. Analyze the provided Resume against the Job Description.
    
    Tasks:
    1. Calculate a Match Score (0-100) based on skills and experience.
    2. Identify "Missing Keywords" (critical skills in the JD not found in the resume).
    3. Provide "Improvement Suggestions" for the student to better align their resume.
    4. Summarize the "Profile Fit" in two sentences.

    Job Description: {job_description}
    Resume Content: {resume_text}
    """

    # Gemini 1.5 Flash is recommended for its speed and high free-tier limits
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            # We define the expected schema directly to ensure 100% JSON reliability
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "score": {"type": "INTEGER"},
                    "missing_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "suggestions": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "profile_fit": {"type": "STRING"}
                },
                "required": ["score", "missing_keywords", "suggestions", "profile_fit"]
            }
        )
    )
    
    return response.text