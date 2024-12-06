import streamlit as st
from ollama import Client
import base64

# Set page configuration
st.set_page_config(
    page_title="Ollama Chat",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ollama_host" not in st.session_state:
    st.session_state.ollama_host = "http://localhost:11434"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "available_models" not in st.session_state:
    st.session_state.available_models = []

if "client" not in st.session_state:
    st.session_state.client = None

# Add new state variable to store uploaded image
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Ollama service address input
    ollama_host = st.text_input("Ollama Service Address", st.session_state.ollama_host)
    
    # Get available models button
    if st.button("Get Available Models"):
        try:
            st.session_state.client = Client(host=ollama_host)
            response = st.session_state.client.list()
            st.session_state.available_models = [model.model for model in response.models]
            st.success("Successfully retrieved model list!")
        except Exception as e:
            st.error(f"Failed to retrieve models: {str(e)}")
    
    # Model selection dropdown
    if st.session_state.available_models:
        selected_model = st.selectbox(
            "Select Model",
            st.session_state.available_models
        )
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.messages = []

# Main interface
st.header("Ollama Chat")

# Create a container to display chat history
chat_container = st.container()

# Create a container at the bottom to place the input box
input_container = st.container()

# Display message history in the chat container
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Place the input box in the bottom container
with input_container:
    # Add image upload component
    uploaded_file = st.file_uploader("Upload Image (Optional)", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        # Convert image data to base64 format
        st.session_state.uploaded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    else:
        st.session_state.uploaded_image = None

    # Chat input
    prompt = st.chat_input("Enter your question")

# Display message history in the chat container
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "images" in message:
                for img in message["images"]:
                    st.image(base64.b64decode(img))

# Handle chat input
if prompt:
    if not st.session_state.selected_model:
        st.error("Please select a model first!")
    else:
        # Add user message
        user_message = {"role": "user", "content": prompt}
        # If there is an image, add it to the message
        if st.session_state.uploaded_image:
            user_message["images"] = [st.session_state.uploaded_image]

        st.session_state.messages.append(user_message)
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                if st.session_state.uploaded_image:
                    st.image(uploaded_file)

        # Add assistant message
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                try:
                    # Use client to chat
                    stream = st.session_state.client.chat(
                        model=st.session_state.selected_model,
                        messages=[{"role": m["role"], "content": m["content"], 
                                   "images": m.get("images", [])} for m in st.session_state.messages],
                        stream=True,
                    )

                    for chunk in stream:
                        full_response += chunk['message']['content']
                        message_placeholder.markdown(full_response + "▌")

                    message_placeholder.markdown(full_response)
                    # Save assistant response
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
