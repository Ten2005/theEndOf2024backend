import supabase
import os
from dotenv import load_dotenv

load_dotenv()

# Add debug prints to check if environment variables are loaded
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")

print(f"URL: {supabase_url}")
print(f"Key: {supabase_key}")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials in environment variables")

supabase = supabase.create_client(supabase_url, supabase_key)

response = supabase.table("log_data").select("content").eq("user_id", "bfed1991-a797-409f-98a4-5301251315fe").order("id").execute()
print([content["content"] for content in response.data])
