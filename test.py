import streamlit as st
import requests
import json

st.title("🧬 Research AI - Direct Connection")

def search_papers(query, limit=3):
    """Search papers using direct Supabase API"""
    try:
        url = st.secrets["https://qqfsxntyinanhutdznts.supabase.co"]
        key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZnN4bnR5aW5hbmh1dGR6bnRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzNjA0MzAsImV4cCI6MjA2NDkzNjQzMH0.zN803irtPItd1Gcob7Q5XI5BSLg_ktfGu23MpIrLznc"]
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        # Search in title first
        search_url = f"{url}/rest/v1/papers?title=ilike.%{query}%&limit={limit}"
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            papers = response.json()
            
            # If no title matches, try abstract
            if not papers:
                search_url = f"{url}/rest/v1/papers?abstract=ilike.%{query}%&limit={limit}"
                response = requests.get(search_url, headers=headers)
                papers = response.json() if response.status_code == 200 else []
            
            return papers
        else:
            st.error(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

def get_all_papers():
    """Get all papers to check connection"""
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
            st.error(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

# Test connection first
st.header("📊 Database Status")
all_papers = get_all_papers()

if all_papers:
    st.success(f"✅ Connected! Found {len(all_papers)} papers in database")
    
    # Show sample papers
    with st.expander("📄 Sample Papers in Database"):
        for paper in all_papers[:3]:
            st.write(f"**{paper['title']}**")
            st.write(f"Authors: {paper['authors']}")
            st.write(f"Journal: {paper['journal']} ({paper['year']})")
            st.write("---")
else:
    st.error("❌ No connection to database")
    st.stop()

# Main search interface
st.header("🔍 Search Research Papers")

question = st.text_input(
    "What would you like to know?",
    placeholder="e.g., 'CRISPR', 'protein engineering', 'gene therapy'"
)

if st.button("Search Papers", type="primary"):
    if question.strip():
        with st.spinner("Searching papers..."):
            papers = search_papers(question)
            
            if papers:
                st.success(f"Found {len(papers)} relevant papers!")
                
                for i, paper in enumerate(papers, 1):
                    with st.expander(f"📄 Paper {i}: {paper['title'][:60]}..."):
                        st.write(f"**Title:** {paper['title']}")
                        st.write(f"**Authors:** {paper['authors']}")
                        st.write(f"**Journal:** {paper['journal']} ({paper['year']})")
                        if paper['abstract']:
                            st.write(f"**Abstract:** {paper['abstract']}")
                        if paper.get('pmid'):
                            st.write(f"**PMID:** {paper['pmid']}")
                
                # Generate simple answer
                st.markdown("---")
                st.markdown("**🤖 AI Summary:**")
                summary = f"Based on {len(papers)} papers in our database:\n\n"
                
                for paper in papers:
                    summary += f"• **{paper['title']}** - {paper['journal']} ({paper['year']})\n"
                
                summary += f"\nThese papers provide information about {question.lower()}. For detailed information, refer to the full papers above."
                
                st.markdown(summary)
            else:
                st.warning("No papers found. Try different keywords like 'CRISPR', 'protein', or 'gene'.")
    else:
        st.warning("Please enter a search term!")

# Sidebar with tips
with st.sidebar:
    st.header("💡 Search Tips")
    st.write("Try these keywords:")
    st.write("• CRISPR")
    st.write("• protein")  
    st.write("• gene")
    st.write("• therapy")
    st.write("• engineering")
    
    st.header("📚 Database Info")
    st.write(f"Total papers: {len(all_papers)}")
    st.write("Source: Research literature")
