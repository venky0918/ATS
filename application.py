from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key="AIzaSyCoS6U8WWaXWloC5sBFFCcco5zJqZCohJ8")

# Define the path to Poppler installed via Homebrew
POPPLER_PATH = "/opt/homebrew/bin"  # Adjust this if Homebrew uses a different location

# Function to get generative response
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

# Function to process uploaded PDF
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            # Convert the PDF to images using pdf2image
            images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=POPPLER_PATH)
            first_page = images[0]

            # Convert the first page to bytes
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Prepare the image data for further processing
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()  # Encode to base64
                }
            ]
            return pdf_parts
        except Exception as e:
            raise RuntimeError(f"Error processing PDF: {e}")
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App
st.set_page_config(page_title="ATS Resume Advisor")
st.header("ATS Insights")
input_text = st.text_area("About the Job", key="input")
uploaded_file = st.file_uploader("Submit Your Resume for Review (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Resume Review and Candidate Assessment")
submit3 = st.button("Resume Match and Optimization Review")

# Input prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager, tasked with reviewing the provided resume against the job description. 
Begin by evaluating the candidate’s qualifications, skills, and experience, and determine how well they align with the role. 
Highlight the key strengths of the applicant, specifically those that directly match the job requirements and demonstrate their suitability for the position. 
Then, identify weaknesses or gaps in the resume where the candidate does not meet the expectations or where additional qualifications or skills are needed. 
Provide insights into the applicant’s potential for growth within the company and suggest any areas where they could benefit from further development. 
Additionally, consider factors such as the candidate’s cultural fit with the organization, based on their experience and skills, and provide an overall recommendation on whether the applicant should move forward in the hiring process. 
Lastly, offer suggestions for the applicant to improve their profile, if applicable.
"""

input_prompt3 = """
You are an advanced ATS (Applicant Tracking System) with expert knowledge in data science and ATS operations. 
Your task is to evaluate the provided resume against the job description. 
First, return a match percentage, indicating how closely the resume aligns with the job description, along with a brief explanation of how you calculated this score. 
Then, provide a comprehensive list of missing keywords, which are relevant skills, certifications, or terms found in the job description but not present in the resume. 
Additionally, identify any overrepresented keywords or skills that might be irrelevant to the role. 
Finally, offer an overall evaluation, summarizing how well the resume fits the job description, highlighting key strengths such as relevant experience and skills, as well as areas for improvement such as missing qualifications, experience gaps, or potential misalignments with the job’s primary needs. 
Include suggestions for how the resume can be optimized to improve alignment with the job description."""

# Handle button clicks
if submit1:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt1, pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please upload the resume.")

elif submit3:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt3, pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please upload the resume.")
