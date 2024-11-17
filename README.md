# mAI-recruiter

## Overview
**mAI-recruiter** is an AI-powered application that assesses your resume against a job description. It supports job descriptions in text, URL, or PDF formats and uses either a local LLM (like Ollama) or external services like Azure OpenAI.

## Project Structure
- `app.py`: The main application script containing the Gradio interface and backend logic.
- `requirements.txt`: A list of Python dependencies required for the project.
- `.env`: Environment file to store API keys and endpoints.
- `README.md`: Project documentation.

## Setup Instructions

### Prerequisites
- Python 3.x installed on your machine.
- API keys for Azure OpenAI if you plan to use it.
- Ollama installed locally if you plan to use a local LLM.

### Install Dependencies
Navigate to the project directory and install the required packages:

```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Update the `.env` file with your actual API keys and endpoints:

```
AZURE_API_KEY=your_actual_azure_api_key
AZURE_OPENAI_ENDPOINT=your_actual_azure_endpoint
AZURE_OPENAI_MODEL_NAME=your_model_name
API_VERSION=your_api_version
```

### Run the Application
Execute the following command to start the application:

```bash
python app.py
```

The Gradio interface should open in your web browser.

## Usage
1. Select the job description input type (Text, URL, or PDF).
2. Provide the job description according to the selected type.
3. Upload your resume in PDF format.
4. Choose whether to use Azure AI or a local LLM.
5. Click the submit button to receive the assessment.

## Dependencies
- gradio
- PyPDF2
- requests
- beautifulsoup4
- lxml
- python-dotenv

## License
This project is licensed under the MIT License.

## Contact
For any questions or suggestions, please open an issue or contact the maintainer.

