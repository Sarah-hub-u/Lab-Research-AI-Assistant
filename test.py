import streamlit as st
import subprocess
import sys

st.title("🧬 Manual Package Installation Test")

# Try to install supabase manually
if st.button("Install Supabase Package"):
    with st.spinner("Installing supabase..."):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
            st.success("✅ Supabase installed!")
        except Exception as e:
            st.error(f"❌ Installation failed: {e}")

# Test import
try:
    from supabase import create_client
    st.success("✅ Supabase imported successfully!")
    
    # Test connection
    url = st.secrets["SUPABASE_URL"] 
    key = st.secrets["SUPABASE_ANON_KEY"]
    
    supabase = create_client(url, key)
    papers = supabase.table('papers').select('id').execute().data
    st.success(f"✅ Connected! Found {len(papers)} papers")
    
except ImportError:
    st.warning("⚠️ Supabase not installed yet - click button above")
except Exception as e:
    st.error(f"❌ Error: {e}")
