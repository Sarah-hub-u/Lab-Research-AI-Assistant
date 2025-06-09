import streamlit as st

st.title("🧬 Package Installation Test")
st.write("Basic Streamlit is working!")

# Test supabase import
try:
    from supabase import create_client
    st.success("✅ Supabase package installed successfully!")
    
    # Test connection
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    
    supabase = create_client(url, key)
    result = supabase.table('papers').select('id').limit(1).execute()
    
    paper_count = len(supabase.table('papers').select('id').execute().data)
    st.success(f"✅ Database connected! Found {paper_count} papers")
    
except ImportError:
    st.error("❌ Supabase package not installed")
except Exception as e:
    st.error(f"❌ Connection error: {e}")
