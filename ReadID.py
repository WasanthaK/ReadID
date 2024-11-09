import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load the Google API key from the .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define upload function
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Configure model parameters
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the Generative Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
)

# Streamlit app layout
st.title("Gemini File Upload and Chat Session")

# File upload section
uploaded_file = st.file_uploader("Choose a file to upload", type=["jpg", "jpeg", "png", "pdf"])

# Input section for chat prompt
user_prompt = st.text_area("Enter your prompt for the model", "read the ID card. top right is the ID number. When reading read and output in original language. you also can release another data set with Key in English and rest in original language")

# Process and display response
if st.button("Submit"):
    if uploaded_file:
        # Save uploaded file locally
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload to Gemini
        file = upload_to_gemini(uploaded_file.name, mime_type="image/jpeg")
        
        # Start chat session
        chat_session = model.start_chat(
            history=[
                {"role": "user", "parts": [file, user_prompt]},
            ]
        )
        
        # Send message to chat session
        response = chat_session.send_message(user_prompt)
        
        # Display the response
        st.write("Response from Model:")
        st.write(response.text)
    else:
        st.warning("Please upload a file before submitting.")
