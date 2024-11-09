import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import sqlite3

# Load the Google API key from the .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the SQLite database connection
conn = sqlite3.connect("accuracy_logs.db")
cursor = conn.cursor()

# Create a table to store accuracy ratings
cursor.execute("""
    CREATE TABLE IF NOT EXISTS accuracy_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        accuracy INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Define upload function
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Define the hardcoded prompt
user_prompt = (
    "read the ID card. top right is the ID number. When reading, "
    "read and output in the original language. You also can release another dataset with the key in English and the rest in the original language."
)

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
st.title("Enadoc Khmer ID Card Reader")

# File upload section
uploaded_file = st.file_uploader("Choose a file to upload", type=["jpg", "jpeg", "png", "pdf"])

# Automatically process the file once it's uploaded
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

    # Horizontal accuracy selection buttons
    st.write("Rate the accuracy of the response:")
    accuracy_levels = [20, 40, 60, 80, 100]

    # Create columns for horizontal button layout
    columns = st.columns(len(accuracy_levels))

    # Display each button in its own column
    for idx, accuracy in enumerate(accuracy_levels):
        with columns[idx]:
            if st.button(f"{accuracy}%"):
                cursor.execute("INSERT INTO accuracy_logs (accuracy) VALUES (?)", (accuracy,))
                conn.commit()
                st.success(f"Accuracy rating of {accuracy}% logged successfully!")

# Close the database connection when the app terminates
conn.close()
