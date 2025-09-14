import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'doctor-patient-reports')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_pdf_to_supabase(file_path, file_name, bucket_name=SUPABASE_BUCKET):
    # Upload the file
    with open(file_path, 'rb') as f:
        res = supabase.storage.from_(bucket_name).upload(file_name, f)
    if res.get('error'):
        raise Exception(f"Supabase upload error: {res['error']['message']}")
    # Get the public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
    return public_url
