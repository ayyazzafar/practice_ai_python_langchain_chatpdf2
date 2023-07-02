# Import necessary modules
import os
import tempfile
import streamlit as st
from streamlit_chat import message
from pdfquery import PDFQuery

# Set the title of the web app
st.set_page_config(page_title="ChatPDF")

# Function to display messages in the chat


def display_messages():
    # Create a subheader titled "Chat"
    st.subheader("Chat")
    # Loop through each message in session state and display it
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    # Create an empty container for the thinking spinner
    st.session_state["thinking_spinner"] = st.empty()

# Function to process the user input


def process_input():
    # Check if there is any user input
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        # Display a spinner while processing the input
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            query_text = st.session_state["pdfquery"].ask(user_text)

        # Append the user's question and the query result to the messages
        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((query_text, False))

# Function to handle file uploads


def read_and_save_file():
    # Reset the knowledge base
    st.session_state["pdfquery"].forget()
    # Reset the messages and user input
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    # Process each uploaded file
    for file in st.session_state["file_uploader"]:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        # Display a spinner while ingesting the file
        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
            st.session_state["pdfquery"].ingest(file_path)
        # Remove the temporary file
        os.remove(file_path)

# Function to check if the OpenAI API key is set


def is_openai_api_key_set() -> bool:
    return len(st.session_state["OPENAI_API_KEY"]) > 0

# Main function to setup the Streamlit application


def main():
    # Initialize session state if not already initialized
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["OPENAI_API_KEY"] = os.environ.get(
            "OPENAI_API_KEY", "")
        # Initialize the PDFQuery instance with the OpenAI API key
        if is_openai_api_key_set():
            st.session_state["pdfquery"] = PDFQuery(
                st.session_state["OPENAI_API_KEY"])
        else:
            st.session_state["pdfquery"] = None

    # Setup the Streamlit interface
    st.header("ChatPDF")
    # Create a text input for the OpenAI API key
    if st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password"):
        # Update the OpenAI API key in the session state if it has changed
        if (
            len(st.session_state["input_OPENAI_API_KEY"]) > 0
            and st.session_state["input_OPENAI_API_KEY"] != st.session_state["OPENAI_API_KEY"]
        ):
            st.session_state["OPENAI_API_KEY"] = st.session_state["input_OPENAI_API_KEY"]
            # Show a warning message if files were previously uploaded
            if st.session_state["pdfquery"] is not None:
                st.warning("Please, upload the files again.")
            # Reset the messages and user input
            st.session_state["messages"] = []
            st.session_state["user_input"] = ""
            # Initialize a new PDFQuery instance with the new API key
            st.session_state["pdfquery"] = PDFQuery(
                st.session_state["OPENAI_API_KEY"])

    # Create a subheader for the file uploader
    st.subheader("Upload a document")
    # Create a file uploader
    st.file_uploader(
        "Upload document",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
        disabled=not is_openai_api_key_set(),
    )

    # Create an empty container for the ingestion spinner
    st.session_state["ingestion_spinner"] = st.empty()

    # Display messages
    display_messages()
    # Create a text input for the user's message
    st.text_input("Message", key="user_input",
                  disabled=not is_openai_api_key_set(), on_change=process_input)

    # Add a divider
    st.divider()
    # Add a link to the source code
    st.markdown(
        "Source code: [Github](https://github.com/Anil-matcha/ChatPDF)")


# If the script is being run directly, call the main function
if __name__ == "__main__":
    main()
