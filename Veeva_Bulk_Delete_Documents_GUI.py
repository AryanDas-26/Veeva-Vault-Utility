#Required to run through Proxy
import os 
os.environ['https_proxy'] = "10.185.190.10:8080"
os.environ['http_proxy'] = "10.185.190.10:8080"
os.environ['ftp_proxy'] = "10.185.190.10:8080"

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from requests.exceptions import RequestException
import requests
import sys
import csv
import time

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.original_stdout.write(message)

    def flush(self):
        pass  # Implementing a flush method is optional

class VeevaAuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Veeva Vault Authentication")
        self.root.configure(bg="blue")

        # Store response as an instance variable
        self.response = None

        # Create Admin Console window
        self.admin_console_window = None

        self.vault_subdomain_address = None  # Initialize to None
        self.api_version = None 

        # Define identifier_dropdown and time_sleep_dropdown as instance attributes
        self.identifier_var = None
        self.time_sleep_var = None


        # Configure style for buttons and frame
        self.style = ttk.Style()
        self.style.configure('Dark.TButton', foreground='white', background='black')  # Set text and background color for buttons
        self.style.configure('Blue.TFrame', background='blue')  # Set background color for the frame

        # Label for the top of the window
        admin_console_label = tk.Label(root, text="Veeva Vault - Authenticator", bg="cyan", fg='black', font=("Calibri", 14, "bold"))
        admin_console_label.pack(side=tk.TOP, fill=tk.X)

        # Frame to hold the input fields
        self.input_frame = ttk.Frame(root, style='Blue.TFrame')
        self.input_frame.pack(side=tk.TOP, pady=10)

        # Initialize csv_file_label attribute
        self.csv_file_label = ttk.Label(root, text="", wraplength=300)

        # Vault Subdomain
        ttk.Label(self.input_frame, text="Vault Subdomain", background="cyan", foreground="black", font=("Calibri", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        self.vault_subdomain_var = tk.StringVar()
        self.vault_subdomain_dropdown = ttk.Combobox(self.input_frame, textvariable=self.vault_subdomain_var, state="readonly")
        self.vault_subdomain_dropdown['values'] = ["Gemstone EAM DEV Sanbox", "Gemstone MVP-2 Sandbox"]
        self.vault_subdomain_dropdown.grid(row=0, column=1, sticky="w", pady=5)
        self.vault_subdomain_dropdown.current(0)  # Set default selection

        # API Version
        ttk.Label(self.input_frame, text="API Version", background="cyan", foreground="black", font=("Calibri", 10, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 5), pady=5)
        self.api_version_var = tk.StringVar()
        self.api_version_dropdown = ttk.Combobox(self.input_frame, textvariable=self.api_version_var, state="readonly")
        self.api_version_dropdown['values'] = ["v22.1", "v23.1"]
        self.api_version_dropdown.grid(row=1, column=1, sticky="w", pady=5)
        self.api_version_dropdown.current(0)  # Set default selection

        # Determine the width for username and password entry fields
        max_width = max(len(option) for option in self.vault_subdomain_dropdown['values'])

        # Username
        ttk.Label(self.input_frame, text="Username", background="cyan", foreground="black", font=("Calibri", 10, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 5), pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.input_frame, textvariable=self.username_var, width=max_width)
        self.username_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Password
        ttk.Label(self.input_frame, text="Password", background="cyan", foreground="black", font=("Calibri", 10, "bold")).grid(row=3, column=0, sticky="w", padx=(0, 5), pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.input_frame, textvariable=self.password_var, show="*", width=max_width)
        self.password_entry.grid(row=3, column=1, sticky="w", pady=5)

        # Authenticate Button
        self.authenticate_button = tk.Button(root, text="Authenticate", command=self.authenticate, fg="white", bg="black", borderwidth=0, relief="flat", font=("Calibri", 10, "bold"))
        self.authenticate_button.pack(side=tk.TOP, padx=10, pady=10)
        self.authenticate_button.configure(highlightthickness=5, highlightcolor="cyan")

        # View Admin Console Button
        self.admin_console_button = tk.Button(root, text="View Admin Console", command=self.view_admin_console, fg="black", bg="yellow", borderwidth=0, relief="flat", font=("Calibri", 10, "bold"))
        self.admin_console_button.pack(side=tk.TOP, padx=10, pady=10)
        self.admin_console_button.configure(highlightthickness=5, highlightcolor="cyan")

        # Exit Button
        self.exit_button = tk.Button(root, text="Exit", command=root.destroy, fg="white", bg="grey", borderwidth=0, relief="raised", font=("Calibri", 10, "bold"))
        self.exit_button.pack(side=tk.TOP, padx=10, pady=10)
        self.exit_button.configure(highlightthickness=5, highlightcolor="cyan")

        # Create Text widget to display console output
        self.console_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10, bg="black", fg="white")
        self.console_output.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

        # Redirect console output to Text widget and normal console
        sys.stdout = ConsoleRedirector(self.console_output)

        # Adjust column weights
        root.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)

    def authenticate(self):
        vault_subdomain = self.vault_subdomain_var.get()
        vault_subdomain_address = ""
        if vault_subdomain == "Gemstone EAM DEV Sanbox":
            vault_subdomain_address = "bayersbx-bayer-ph-clinical-eam-dev.veevavault.com"
        elif vault_subdomain == "Gemstone MVP-2 Sandbox":
            vault_subdomain_address = "bayersbx-bayer-ph-clinical-mvp-2-sandbox.veevavault.com"

        username = self.username_var.get()
        password = self.password_var.get()

        # Configuration
        #api_version = "v22.1"  # Replace with the desired API version
        api_version = self.api_version_var.get()
        

        # Authentication endpoint
        auth_url = f"https://{vault_subdomain_address}/api/{api_version}/auth"

        # Prepare authentication request
        auth_data = {"username": username, "password": password}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Send authentication request and handle potential errors
        try:
            response = requests.post(auth_url, headers=headers, data=auth_data)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            session_id = response.json()["sessionId"]
            print("Authentication Successful\n \nVeeva Vault:", vault_subdomain_address, "\n\nSession ID:", session_id)
            # Use the session ID in subsequent Vault API calls
            headers = {"Authorization": f"Bearer {session_id}"}
            self.session_id = session_id  # Set session_id attribute
            # Call other functions requiring authentication here
            self.response = True
        except requests.exceptions.RequestException as e:
            print(f"Authentication request failed: {e}")
        
        return vault_subdomain_address, api_version

    def view_admin_console(self):
        if self.response:
            self.admin_console_window = tk.Toplevel(self.root)
            self.admin_console_window.title("Admin Console")
            self.admin_console_window.configure(bg="blue")

            admin_console_label = tk.Label(self.admin_console_window, text="Admin Console", bg = "cyan", fg='black', font=("Calibri", 14, "bold"))
            admin_console_label.pack(side=tk.TOP, fill=tk.X)

            bulk_document_button = tk.Button(self.admin_console_window, text="Bulk Document Deletion", command=self.bulk_document_deletion, fg="white", bg="black", borderwidth=0, relief="flat")
            bulk_document_button.pack(pady=10)
            bulk_document_button.configure(highlightthickness=5, highlightcolor="cyan")

            self.console_output_admin = scrolledtext.ScrolledText(self.admin_console_window, wrap=tk.WORD, width=40, height=10, bg="black", fg="white")
            self.console_output_admin.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

            # Exit Button
            self.exit_button = tk.Button(self.admin_console_window, text="Exit", command=self.admin_console_window.destroy, fg="white", bg="grey", borderwidth=0, relief="raised", font=("Calibri", 10, "bold"))
            self.exit_button.pack(side=tk.TOP, padx=10, pady=10)
            self.exit_button.configure(highlightthickness=5, highlightcolor="cyan")

        else:
            print("Please authenticate to view the Admin console.")

    def bulk_document_deletion(self):
        bulk_deletion_window = tk.Toplevel(self.admin_console_window)
        bulk_deletion_window.title("Bulk Document Deletion")
        bulk_deletion_window.configure(bg="blue")

        # Create Text widget to display console output
        console_output_admin = scrolledtext.ScrolledText(bulk_deletion_window, wrap=tk.WORD, width=40, height=10, bg="black", fg="white")
        console_output_admin.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

        # Redirect console output to Text widget and normal console
        sys.stdout = ConsoleRedirector(console_output_admin)

        bulk_deletion_label = tk.Label(bulk_deletion_window, text="Bulk Document Deletion", bg = "cyan", fg='black', font=("Calibri", 14, "bold"))
        bulk_deletion_label.pack(side=tk.TOP, fill=tk.X)

        # Frame to hold the elements
        frame = ttk.Frame(bulk_deletion_window, padding=10, style='Blue.TFrame')
        frame.pack(fill=tk.BOTH, expand=True)

        # Centrally aligned Button for opening file
        open_file_button = ttk.Button(frame, text="Open File", command=self.open_csv_file)
        open_file_button.pack(pady=(0, 10))

        # Frame for identifier and buffer time selection
        selection_frame = ttk.Frame(frame, padding=(10, 0), style='Blue.TFrame')
        selection_frame.pack(side=tk.TOP, pady=10)

        # Label and Dropdown for selecting identifier
        select_identifier_label = ttk.Label(selection_frame, text="Select Identifier", background="cyan", foreground="black", font=("Calibri", 10, "bold"))
        select_identifier_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)

        self.identifier_var = tk.StringVar()
        identifier_dropdown = ttk.Combobox(selection_frame, textvariable=self.identifier_var, state="readonly")
        identifier_dropdown['values'] = ["id", "external_id"]
        identifier_dropdown.current(0)
        identifier_dropdown.grid(row=0, column=1, sticky="w", padx=10)

        # Label and Dropdown for selecting buffer time
        select_buffer_label = ttk.Label(selection_frame, text="Select Buffer Time (in sec)", background="cyan", foreground="black", font=("Calibri", 10, "bold"))
        select_buffer_label.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=5)

        self.time_sleep_var = tk.StringVar(value="20")  # Default value set to 20
        time_sleep_dropdown = ttk.Combobox(selection_frame, textvariable=self.time_sleep_var, state="readonly")
        time_sleep_dropdown['values'] = ["5", "10", "15", "20", "25", "30"]
        time_sleep_dropdown.grid(row=1, column=1, sticky="w", padx=10)

        # Button to perform bulk deletion
        bulk_delete_button = tk.Button(frame, text="Bulk Delete Documents", command=self.perform_bulk_deletion, fg="white", bg="black", borderwidth=0, relief="flat")
        bulk_delete_button.pack(side=tk.TOP, padx=10, pady=(20, 10))
        bulk_delete_button.configure(highlightthickness=5, highlightcolor="cyan")

        # Button to view status files
        view_status_button = tk.Button(frame, text="View Status Files", command=self.view_status_files, fg="black", bg="yellow", borderwidth=0, relief="flat")
        view_status_button.pack(side=tk.TOP, padx=10, pady=10)
        view_status_button.configure(highlightthickness=5, highlightcolor="cyan")

        # Exit Button
        exit_button = tk.Button(frame, text="Exit", command=bulk_deletion_window.destroy, fg="white", bg="grey", borderwidth=0, relief="raised", font=("Calibri", 10, "bold"))
        exit_button.pack(side=tk.TOP, padx=10, pady=10)
        exit_button.configure(highlightthickness=5, highlightcolor="cyan")

        # Adjust column weights
        bulk_deletion_window.grid_rowconfigure(0, weight=1)
        bulk_deletion_window.grid_columnconfigure(0, weight=1)

    def open_csv_file(self):
        csv_file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if csv_file_path:
            # Update the label with the selected file path
            self.csv_file_label.config(text=csv_file_path)

    def perform_bulk_deletion(self):
        # Get selected CSV file path and other parameters
        csv_file_path = self.csv_file_label.cget("text")
        identifier = self.identifier_var.get()
        time_sleep_var = self.time_sleep_var.get()

        #time_sleep_var = int(time_sleep_var)

        # Configuration (replace with your values)
        id_column_name = identifier  # Adjust if the ID column has a different name
        vault_subdomain_address, api_version = self.authenticate()
        

        # Headers for the API request
        headers = {
            "Authorization": f"Bearer {self.session_id}",
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }

        # Delete documents endpoint (accommodating potential workaround)
        delete_documents_url = f"https://{vault_subdomain_address}/api/{api_version}/objects/documents/batch"
        if not requests.delete("https://httpbin.org/delete", data="").ok:  # Test DELETE support
            delete_documents_url += "?_method=DELETE"  # Apply workaround if needed

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Read the header row
                id_column_index = header.index(id_column_name)  # Get the index of the ID column

                document_ids = []
                for row in reader:
                    document_ids.append(row[id_column_index])  # Extract IDs from each row

                # Delete documents in batches of 500
                batch_size = 500
                for i in range(0, len(document_ids), batch_size):
                    batch = document_ids[i:i + batch_size]
                    csv_data = f"{id_column_name}\n" + "\n".join([f"{doc_id}" for doc_id in batch])

                    try:
                        response = requests.delete(delete_documents_url, headers=headers, data=csv_data)  # Delete API Call
                        response.raise_for_status()  # Raise exception for non-200 status codes
                        print(f"Deletion Response (Batch {i//batch_size + 1}):", response.text)
                    except RequestException as e:
                        print(f"Failed to delete documents in batch: {e}")
                        exit()

                    # Split response text into lines assuming a comma-separated format
                    response_lines = response.text.splitlines()

                    with open(f"Deletion_Response_Batch_{i//batch_size + 1}.csv", "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(csv.reader(response_lines))  # Write as CSV

                    # Sleep for Buffer seconds after each batch
                    time.sleep(time_sleep_var)

        except FileNotFoundError:
            print(f"CSV file not found at path: {csv_file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def view_status_files(self):
        # Open status files or perform any additional action
        csv_file_path = self.csv_file_label.cget("text")
        directory = os.path.dirname(csv_file_path)
        os.system(f'explorer "{os.path.abspath(directory)}"')
        print(f"Viewing status files for CSV file: {csv_file_path}")

def main():
    root = tk.Tk()
    app = VeevaAuthenticationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()