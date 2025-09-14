import os
from boxsdk import Client, OAuth2

# Utility to upload a PDF to Box and return the shareable link
def upload_pdf_to_box(file_path, file_name, developer_token, parent_folder_id='0'):
    oauth2 = OAuth2(
        client_id=None,  # Not needed for developer token
        client_secret=None,  # Not needed for developer token
        access_token=developer_token
    )
    client = Client(oauth2)
    folder = client.folder(folder_id=parent_folder_id)
    # Upload file
    uploaded_file = folder.upload(file_path, file_name=file_name)
    # Create a shared link
    shared_link = uploaded_file.get_shared_link(access='open')
    return shared_link

# Example usage:
# link = upload_pdf_to_box('/path/to/file.pdf', 'report.pdf', 'YOUR_DEVELOPER_TOKEN')
# print(link)
