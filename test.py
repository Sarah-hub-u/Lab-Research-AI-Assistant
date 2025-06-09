import streamlit as st

st.title("🧬 Simple Test")
st.write("If you see this, Streamlit is working!")

# Test supabase import
try:
    from supabase import create_client
    st.success("✅ Supabase import successful!")
except ImportError as e:
    st.error(f"❌ Supabase import failed: {e}")

# Test connection
try:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    
    if url and key:
        supabase = create_client(url, key)
        result = supabase.table('papers').select('id').limit(1).execute()
        st.success("✅ Database connection successful!")
    else:
        st.warning("⚠️ Secrets not found")
except Exception as e:
    st.error(f"❌ Connection failed: {e}")
