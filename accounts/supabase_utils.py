import re
def sanitize_filename(filename):
    # Replace any non-ASCII or problematic characters with underscore
    return re.sub(r'[^A-Za-z0-9._-]', '_', filename)
import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'doctor-patient-reports')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_pdf_to_supabase(file_path, file_name, bucket_name=SUPABASE_BUCKET):
    safe_name = sanitize_filename(file_name)
    with open(file_path, 'rb') as f:
        res = supabase.storage.from_(bucket_name).upload(safe_name, f)
    if res.get('error'):
        raise Exception(f"Supabase upload error: {res['error']['message']}")
    public_url = supabase.storage.from_(bucket_name).get_public_url(safe_name)
    return public_url
