import streamlit as st
import requests
import json

st.title("🧬 Research AI - Working Version")

def get_papers():
    """Get papers from Supabase"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{url}/rest/v1/papers?select=*", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Database error: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

def search_papers(query):
    """Search papers by title"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        # Search in title
        search_url = f"{url}/rest/v1/papers?title=ilike.%{query}%"
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
            
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# Main app
st.header("📊 Database Status")
papers = get_papers()

if papers:
    st.success(f"✅ Connected! Found {len(papers)} papers")
    
    # Show papers
    with st.expander("📄 Papers in Database"):
        for paper in papers:
            st.write(f"**{paper.get('title', 'No title')}**")
            st.write(f"Authors: {paper.get('authors', 'No authors')}")
            st.write("---")
else:
    st.error("❌ No papers found")

# Search interface
st.header("🔍 Search Papers")
search_query = st.text_input("Search for:", placeholder="CRISPR, protein, gene")

if st.button("Search"):
    if search_query:
        results = search_papers(search_query)
        if results:
            st.success(f"Found {len(results)} papers!")
            for paper in results:
                with st.expander(paper.get('title', 'Untitled')[:50] + "..."):
                    st.write(f"**Authors:** {paper.get('authors', 'Unknown')}")
                    st.write(f"**Journal:** {paper.get('journal', 'Unknown')}")
                    if paper.get('abstract'):
                        st.write(f"**Abstract:** {paper['abstract'][:200]}...")
        else:
            st.warning("No papers found for that search")
