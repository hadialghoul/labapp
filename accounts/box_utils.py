
import os
from boxsdk import Client, JWTAuth
from django.conf import settings


# Utility to upload a PDF to Box and return the shareable link using JWT auth
def upload_pdf_to_box(file_path, file_name, parent_folder_id='0'):
    # Load Box JWT config path from Django settings
    config_path = getattr(settings, 'BOX_CONFIG_PATH', None)
    if not config_path or not os.path.exists(config_path):
        raise Exception(f"Box config file not found at {config_path}. Set BOX_CONFIG_PATH in your settings or environment.")

    auth = JWTAuth.from_settings_file(config_path)
    client = Client(auth)
    folder = client.folder(folder_id=parent_folder_id)
    # Upload file
    uploaded_file = folder.upload(file_path, file_name=file_name)
    # Create a shared link
    shared_link = uploaded_file.get_shared_link(access='open')
    return shared_link

# Example usage:
# link = upload_pdf_to_box('/path/to/file.pdf', 'report.pdf')
# print(link)
