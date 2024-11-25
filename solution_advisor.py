# import streamlit as st
# import requests
# import webbrowser

# # Title and Description
# st.title("Solution Advisor")
# st.write("Input your Behavior Prompt and Roadmap to start talking with the AI chatbot!")

# # Layout: Two Columns
# col1, col2 = st.columns(2)

# with col1:
#     st.header("Behavior Prompt")
#     behavior_prompt = st.text_area("Enter your prompt here:", placeholder="E.g., Explain AI adoption challenges")

# with col2:
#     st.header("Roadmap")
#     roadmap_text = st.text_area("Enter your roadmap here:", placeholder="E.g., Timeline, milestones, etc.")
#     uploaded_file = st.file_uploader("Upload Roadmap File (Optional)", type=["txt", "pdf", "docx"])

# # Submit Button
# if st.button("Submit"):
#     # Handle file upload if provided
#     roadmap_content = ""
#     if uploaded_file:
#         roadmap_content = uploaded_file.read().decode('utf-8', errors='ignore') if uploaded_file.type.startswith("text/") else "File uploaded but not displayed."
#     elif roadmap_text:
#         roadmap_content = roadmap_text
    
#     # Check if necessary fields are filled
#     if not behavior_prompt:
#         st.warning("Please enter a Behavior Prompt.")
#     elif not roadmap_content:
#         st.warning("Please enter or upload a Roadmap.")
#     else:
#         # Payload
#         payload = {
#             "behavior_prompt": behavior_prompt,
#             "roadmap": roadmap_content
#         }
        
#         # API call
#         endpoint = "https://visaroadmap-pipeline-pratik1-1001.fly.dev/"
#         try:
#             response = requests.post(endpoint, json=payload)
#             if response.status_code == 200:
#                 # json_response=response.json()
#                 st.success("Connected! You can now start talking with the AI chatbot.")
#                 st.write("Response from server:", response.json())
#                 # webbrowser.open_new_tab(json_response["room_url"])
#             else:
#                 st.error(f"Error: Unable to connect. Status Code: {response.status_code}")
#                 st.write(response.text)
#         except Exception as e:
#             st.error(f"An error occurred: {e}")



import streamlit as st
import requests

# Title and Description
st.title("Solution Advisor")
st.write("Input your Behavior Prompt and Roadmap to start talking with the AI chatbot!")

# Layout: Two Columns
col1, col2 = st.columns(2)

with col1:
    st.header("Behavior Prompt")
    behavior_prompt = st.text_area("Enter your prompt here:", placeholder="E.g., Explain AI adoption challenges")

with col2:
    st.header("Roadmap")
    roadmap_text = st.text_area("Enter your roadmap here:", placeholder="E.g., Timeline, milestones, etc.")
    uploaded_file = st.file_uploader("Upload Roadmap File (Optional)", type=["txt", "pdf", "docx"])

# Submit Button
if st.button("Submit"):
    # Handle file upload if provided
    roadmap_content = ""
    if uploaded_file:
        roadmap_content = uploaded_file.read().decode('utf-8', errors='ignore') if uploaded_file.type.startswith("text/") else "File uploaded but not displayed."
    elif roadmap_text:
        roadmap_content = roadmap_text
    
    # Check if necessary fields are filled
    if not behavior_prompt:
        st.warning("Please enter a Behavior Prompt.")
    elif not roadmap_content:
        st.warning("Please enter or upload a Roadmap.")
    else:
        # Payload
        payload = {
            "behavior_prompt": behavior_prompt,
            "roadmap": roadmap_content
        }
        
        # API call
        endpoint = "https://visaroadmap-pipeline-pratik1-1001.fly.dev/"
        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                data = response.json()
                room_url = data.get("room_url")
                
                if room_url:
                    st.success("Connected! You can now join the room.")
                    st.markdown(f"[Join Now]({room_url})", unsafe_allow_html=True)
                else:
                    st.error("Room URL not found in the response.")
            else:
                st.error(f"Error: Unable to connect. Status Code: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
