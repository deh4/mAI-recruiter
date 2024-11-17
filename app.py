import gradio as gr
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import requests
from bs4 import BeautifulSoup  # Added for web scraping

load_dotenv()  # Load all environment variables

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_OPENAI_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME")
API_VERSION = os.getenv("API_VERSION")

# Function to generate response using Ollama
def generate_response(prompt, model="llama3.1:latest"):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "system": "You are an experienced Application Tracking System (ATS).",
        "stream": True  # Enable streaming response
    }
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                line_decoded = line.decode("utf-8")
                response_json = json.loads(line_decoded)
                yield response_json.get("response", "")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Function to generate response using Azure OpenAI
def generate_azure_response(prompt):
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY,
    }
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an experienced Application Tracking System (ATS)."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }
    AZURE_ENDPOINT = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_MODEL_NAME}/chat/completions?api-version={API_VERSION}"

    response = requests.post(AZURE_ENDPOINT, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            return response_data["choices"][0].get("message", {}).get("content", "").strip()
        else:
            raise Exception("No choices found in Azure response")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Extract text from PDF
def extract_pdf_text(file_path):
    reader = pdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Extract text from URL
def extract_url_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    text = ' '.join(soup.stripped_strings)
    return printf(text)

# Function to fetch installed Ollama models using /api/tags endpoint
def fetch_ollama_models():
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            # Extract the names of the models for the dropdown
            return [model["name"] for model in models_data]
        else:
            return ["Error: Unable to fetch models"]
    except Exception as e:
        return [f"Error: {str(e)}"]

# Main processing function (updated to include model selection)
def process_resume(jd_input_type, jd_text_input, jd_file_input, resume_file, selected_model, use_azure=False):
    # Process job description based on input type
    if jd_input_type == "Text":
        jd_text = jd_text_input
    elif jd_input_type == "URL":
        jd_text = extract_url_text(jd_text_input)
    elif jd_input_type == "PDF":
        if jd_file_input is not None:
            jd_text = extract_pdf_text(jd_file_input.name)
        else:
            return "Please upload a PDF file for the job description."
    else:
        return "Invalid job description input type."

    # Process the resume file
    if resume_file is not None:
        resume_text = extract_pdf_text(resume_file.name)
    else:
        return "Please upload your resume in PDF format."

    # Updated Prompt with Cognitive Considerations
    input_prompt = f"""
    Your task is to act as an executive recruiter specializing in data, AI, software, and cloud domains. Evaluate candidate resumes according to given job descriptions, identify gaps, and suggest improvements critically and clearly.

    Detailed Instructions:
    - You are an executive recruiter specializing in data, AI, software, and cloud domains. You have broad experience with assessing various roles within these fields.
    - You will be provided with a job description and an applicant’s resume.
    - Your task is to: 
        1. Extract key assessment topics based on the job description provided.
        2. Critically assess the provided resume against the assessment topics.
        3. Assign a matching score out of 100 points based on your evaluation.

    Assessment Specifics:
    - Extract key responsibilities, technical skills, and soft skills from the job description that are most critical for the role.
    - Once you have the assessment topics, compare the resume with each topic.
      - Be direct and critical in your comparison. Do not soften your feedback for politeness. 
      - A remote match or loosely aligned experience should be deemed insufficient.
      - Provide a direct matching score on how well the candidate meets each key topic, then calculate an overall matching score out of 100.
      
    Feedback and Improvement Suggestions:
    - Provide detailed feedback on both strengths and shortcomings.
    - For shortcomings, provide actionable suggestions on how to improve the resume. Address:
      1. The key elements that hiring managers are looking for at first glance.
      2. How these elements should be harmonized on the resume to enhance clarity and impact.

    # Steps

    1. Extract key assessment topics from the job description.
       - Focus on responsibilities, technical skills, and required experience.
    2. Assess the candidate’s resume based on the extracted topics:
       - Evaluate each element of the resume against the extracted topics.
       - Assign a score (between 0-100) based on how well the resume matches each topic.
       - Be direct in your criticism; unnecessary courtesy is not needed.
    3. Provide comprehensive improvement suggestions:
       - Identify key areas needing improvement.
       - Suggest specific changes/approaches to improve based on hiring priorities.

    # User input
    - **Job Description**:
    {jd_text}

    - **Candidate's Resume**:
    {resume_text}

    # Output Format

    The output should have the following format in markdown:
    
    ### About the job
    - **Job title**:
    - **Job summary**:

    ### Matching Score
    - **Overall Score**: [Matching Score out of 100]

    ### Assessment Breakdown
    - **Topic 1 (e.g., Technical Skills)**:
      - **Score**: [Score out of 100]
      - **Feedback**: [Detailed feedback]
    - **Topic 2 (e.g., Soft Skills)**:
      - **Score**: [Score out of 100]
      - **Feedback**: [Detailed feedback]
    (add as many as needed)
    ### Update for executive summary section 
      - [Reformulate the executive summary section without adding new skill or knowledge, stick to the original content, but re-order it based on the most important needs of the job description

    ### Update for core competencies
      - [Reorder the core competencies section, don't add any new skill or knowledge, stick to the original content, but re-order it based on the most important competencies needed of the job description

    """

# Generate response
    if use_azure:
        response = generate_azure_response(input_prompt)
    else:
        response = ""
        for partial_response in generate_response(input_prompt, model=selected_model):
            response += partial_response

    return response

# Gradio app

def update_inputs(jd_input_type):
    if jd_input_type == "PDF":
        return {
            jd_text_input: gr.update(visible=False),
            jd_file_input: gr.update(visible=True),
        }
    else:  # "Text" or "URL"
        placeholder_text = "Paste the job description text here" if jd_input_type == "Text" else "Enter the job description URL here"
        label_text = f"Enter Job Description {jd_input_type}"
        return {
            jd_text_input: gr.update(visible=True, placeholder=placeholder_text, label=label_text),
            jd_file_input: gr.update(visible=False),
        }

with gr.Blocks() as iface:
    gr.Markdown("# mAI-recruiter\nAssess your resume against a job description.")

    with gr.Row():
        with gr.Column():
            # Input components
            jd_input_type = gr.Radio(
                choices=["Text", "URL", "PDF"],
                label="Job Description Input Type",
                value="Text"
            )

            jd_text_input = gr.Textbox(
                label="Enter Job Description Text",
                lines=5,
                placeholder="Paste the job description text here"
            )

            jd_file_input = gr.File(
                label="Upload Job Description PDF",
                file_types=['.pdf'],
                visible=False  # Initially hidden
            )

            resume_file = gr.File(
                label="Upload Your Resume (PDF)",
                file_types=['.pdf']
            )

            # Dropdown for model selection
            model_dropdown = gr.Dropdown(
                label="Select Ollama Model",
                choices=fetch_ollama_models(),
                value="llama3.1:latest"  # Default value
            )

            use_azure = gr.Checkbox(
                label="Use Azure AI",
                value=False
            )

            submit_button = gr.Button("Submit")
        with gr.Column():
            # Output component
            output = gr.Textbox(
                label="Response",
                lines=25
            )

    # Update inputs when jd_input_type changes
    jd_input_type.change(
        fn=update_inputs,
        inputs=jd_input_type,
        outputs=[jd_text_input, jd_file_input]
    )

    # Define what happens when submit_button is clicked
    submit_button.click(
        fn=process_resume,
        inputs=[jd_input_type, jd_text_input, jd_file_input, resume_file, model_dropdown, use_azure],
        outputs=output
    )

iface.launch()