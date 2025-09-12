import streamlit as st
import pandas as pd
import requests
import os
import time
import csv


# Vault subdomain options
vault_options = {
    "Gemstone PH Clinical Sandbox": "bayersbx-bayer-ph-clinical-mvp-2-sandbox.veevavault.com",
    "Gemstone PH Clinical Testing": "bayersbx-bayer-ph-clinical-testing.veevavault.com",
    "Gemstone PH Clinical Training": "bayersbx-bayer-ph-clinical-training.veevavault.com",
    "Gemstone PH Clinical Validation": "bayersbx-bayer-ph-clinical-validation.veevavault.com",
    "Gemstone PH Clinical Integration": "bayersbx-bayer-ph-clinical-mvp-2-integration.veevavault.com"
}

# Initialize session state for session ID
if 'session_id' not in st.session_state:
    st.session_state.session_id = None

# Streamlit UI
st.title("Veeva Vault Bulk Document Deletion")

# User input for authentication
username = st.text_input("Username")
password = st.text_input("Password", type='password')
vault_subdomain = st.selectbox("Select Vault Subdomain", list(vault_options.keys()) + ["Other"], index=0)

if vault_subdomain == "Other":
    vault_subdomain = st.text_input("Enter Vault Subdomain", value="")

# API version
api_version = "v25.1"

# File upload
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# Buffer time selection
buffer_time = st.selectbox("Select Buffer Time (seconds)", [5, 10, 15, 20])

def authenticate():
    """Authenticate with the API and return the session ID."""
    auth_url = f"https://{vault_subdomain}/api/{api_version}/auth"
    auth_data = {"username": username, "password": password}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    try:
        response = requests.post(auth_url, headers=headers, data=auth_data)
        response.raise_for_status()
        session_id = response.json().get("sessionId")
        st.session_state.session_id = session_id  # Save session ID in session state
        st.success("Authenticated successfully.")
        return session_id
    except requests.exceptions.RequestException as e:
        st.error(f"Authentication failed: {e}")
        return None

def get_headers():
    """Return headers with valid session ID."""
    if st.session_state.session_id:
        return {
            "Authorization": st.session_state.session_id,
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }
    return None

if st.button("Authenticate and Delete Documents"):
    if username and password:
        # Authenticate and get the session ID
        session_id = authenticate()
        
        if session_id and uploaded_file is not None:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            if 'id' not in df.columns:
                st.error("CSV file must contain an 'id' column.")
                st.stop()

            document_ids = df['id'].tolist()

            # Delete documents in batches
            batch_size = 500
            response_data = []

            for i in range(0, len(document_ids), batch_size):
                batch = document_ids[i:i + batch_size]
                csv_data = f"id\n" + "\n".join(map(str, batch))  # Prepare CSV data for the current batch

                # Prepare headers with valid session ID
                headers = get_headers()
                delete_documents_url = f"https://{vault_subdomain}/api/{api_version}/objects/documents/batch"

                try:
                    response = requests.delete(delete_documents_url, headers=headers, data=csv_data)  # Send CSV data
                    response.raise_for_status()
                    st.success(f"Batch {i // batch_size + 1} deleted successfully.")
                    response_data.append(response.text.splitlines())
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to delete documents in batch {i // batch_size + 1}: {e}")
                    st.stop()

                # Sleep for the selected buffer time
                time.sleep(buffer_time)

            # Merge response data into a single CSV file
            merged_file_path = "Response.csv"
            with open(merged_file_path, "w", newline="") as f:
                writer = csv.writer(f)
                for response_lines in response_data:
                    writer.writerows(csv.reader(response_lines))

            # Provide download link for the merged file
            with open(merged_file_path, "rb") as f:
                st.download_button("Download Merged Response CSV", f, file_name=merged_file_path)

        else:
            st.error("Please upload a CSV file.")
    else:
        st.error("Please enter both username and password.")