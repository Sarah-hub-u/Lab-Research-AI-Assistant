import streamlit as st

st.title("🧬 Connection Test")
st.write("Basic Streamlit is working!")

# Test secrets
url = st.secrets.get("SUPABASE_URL", "Not found")
key = st.secrets.get("SUPABASE_ANON_KEY", "Not found")

st.write(f"URL: {url[:20]}..." if len(url) > 20 else url)
st.write(f"Key: {key[:20]}..." if len(key) > 20 else key)

if "supabase.co" in url and len(key) > 50:
    st.success("✅ Secrets are configured correctly!")
else:
    st.error("❌ Secrets not configured properly")
