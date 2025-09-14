import re
def sanitize_filename(filename):
    # Replace any non-ASCII or problematic characters with underscore
    return re.sub(r'[^A-Za-z0-9._-]', '_', filename)
import os
from supabase import create_client, Client



    # File removed as Supabase functionality is no longer needed.
