import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Advanced Research AI",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Advanced Research AI Assistant")
st.markdown("*Your intelligent research companion with advanced analytics*")

def get_papers():
    """Get papers from Supabase"""
    try:
        url = st.secrets["https://qqfsxntyinanhutdznts.supabase.co"]
        key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZnN4bnR5aW5hbmh1dGR6bnRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzNjA0MzAsImV4cCI6MjA2NDkzNjQzMH0.zN803irtPItd1Gcob7Q5XI5BSLg_ktfGu23MpIrLznc"]
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{url}/rest/v1/papers?select=*", headers=headers)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def advanced_search(query, papers, search_mode):
    """Enhanced search with multiple modes"""
    results = []
    query_lower = query.lower()
    
    for paper in papers:
        score = 0
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        
        if search_mode == "Title Only":
            if query_lower in title:
                score = 1.0
        elif search_mode == "Abstract Only":
            if query_lower in abstract:
                score = 0.8
        else:  # "Smart Search"
            if query_lower in title:
                score += 1.0
            if query_lower in abstract:
                score += 0.5
            
            # Bonus for recent papers
            if paper.get('year', 0) >= 2023:
                score += 0.2
        
        if score > 0:
            paper['relevance_score'] = score
            results.append(paper)
    
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)

def create_research_dashboard(papers):
    """Create visual research insights"""
    
    # Papers by year
    years = {}
    journals = {}
    
    for paper in papers:
        year = paper.get('year', 2024)
        journal = paper.get('journal', 'Unknown')[:30]  # Truncate long names
        
        years[year] = years.get(year, 0) + 1
        journals[journal] = journals.get(journal, 0) + 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        if years:
            fig_years = px.bar(
                x=list(years.keys()), 
                y=list(years.values()),
                title="📅 Publications by Year",
                labels={'x': 'Year', 'y': 'Number of Papers'}
            )
            st.plotly_chart(fig_years, use_container_width=True)
    
    with col2:
        if journals:
            top_journals = dict(sorted(journals.items(), key=lambda x: x[1], reverse=True)[:8])
            fig_journals = px.pie(
                values=list(top_journals.values()),
                names=list(top_journals.keys()),
                title="📚 Top Journals"
            )
            st.plotly_chart(fig_journals, use_container_width=True)

# Main app
papers = get_papers()

# Sidebar
with st.sidebar:
    st.header("🔧 Research Tools")
    
    # Database stats
    st.subheader("📊 Database")
    if papers:
        st.metric("Total Papers", len(papers))
        recent_papers = [p for p in papers if p.get('year', 0) >= 2023]
        st.metric("Recent Papers (2023+)", len(recent_papers))
        
        # Quick filters
        st.subheader("🎯 Quick Filters")
        if st.button("🔬 CRISPR Research"):
            st.session_state.search_query = "CRISPR"
        if st.button("🧪 Protein Engineering"):
            st.session_state.search_query = "protein engineering"
        if st.button("🦠 Gene Therapy"):
            st.session_state.search_query = "gene therapy"
        if st.button("⚙️ Bioengineering"):
            st.session_state.search_query = "bioengineering"
    
    # Research insights
    st.subheader("💡 Research Tips")
    st.info("💡 Use specific terms like 'CRISPR-Cas9' or 'protein folding'")
    st.info("🎯 Try 'Smart Search' for best results")
    st.info("📊 Check the analytics below for research trends")

# Main interface
if papers:
    st.success(f"✅ Connected! Database contains {len(papers)} research papers")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search Research Literature",
            value=st.session_state.get('search_query', ''),
            placeholder="e.g., 'CRISPR gene editing', 'protein folding', 'bioengineering applications'",
            key="main_search"
        )
    
    with col2:
        search_mode = st.selectbox(
            "Search Mode",
            ["Smart Search", "Title Only", "Abstract Only"]
        )
    
    # Search button and results
    if st.button("🚀 Search Papers", type="primary") or search_query:
        if search_query:
            with st.spinner("🧠 Analyzing research papers..."):
                results = advanced_search(search_query, papers, search_mode)
                
                if results:
                    st.success(f"📋 Found {len(results)} relevant papers!")
                    
                    # Results summary
                    avg_year = sum(p.get('year', 2024) for p in results) / len(results)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Papers Found", len(results))
                    with col2:
                        st.metric("Avg. Publication Year", f"{avg_year:.0f}")
                    with col3:
                        high_relevance = len([r for r in results if r.get('relevance_score', 0) > 0.8])
                        st.metric("High Relevance", high_relevance)
                    
                    # Display results
                    for i, paper in enumerate(results[:10], 1):  # Top 10 results
                        relevance = paper.get('relevance_score', 0)
                        
                        with st.expander(f"📄 #{i} - {paper.get('title', 'Untitled')[:80]}... ⭐{relevance:.2f}"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**Authors:** {paper.get('authors', 'Unknown')}")
                                st.write(f"**Journal:** {paper.get('journal', 'Unknown')} ({paper.get('year', 'Unknown')})")
                                if paper.get('abstract'):
                                    st.write(f"**Abstract:** {paper['abstract'][:400]}...")
                                if paper.get('pmid'):
                                    st.write(f"**PubMed ID:** {paper['pmid']}")
                            
                            with col2:
                                st.metric("Relevance", f"{relevance:.3f}")
                                if paper.get('year', 0) >= 2023:
                                    st.success("🆕 Recent")
                                
                                # Quick actions
                                if st.button(f"🔗 Similar Papers", key=f"similar_{i}"):
                                    st.session_state.search_query = paper.get('title', '')[:30]
                                    st.rerun()
                
                else:
                    st.warning("🔍 No papers found. Try different keywords or search modes.")
    
    # Research Dashboard
    st.markdown("---")
    st.header("📊 Research Analytics Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🔍 Search Analytics", "💡 Insights"])
    
    with tab1:
        create_research_dashboard(papers)
    
    with tab2:
        st.subheader("🎯 Popular Search Terms")
        search_terms = ["CRISPR", "protein", "gene therapy", "bioengineering", "synthetic biology"]
        
        search_results = {}
        for term in search_terms:
            results = advanced_search(term, papers, "Smart Search")
            search_results[term] = len(results)
        
        fig = px.bar(
            x=list(search_results.keys()),
            y=list(search_results.values()),
            title="📊 Papers Available by Research Area"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("💡 Research Insights")
        
        # Extract insights
        total_papers = len(papers)
        recent_papers = len([p for p in papers if p.get('year', 0) >= 2023])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Database Size", f"{total_papers:,}")
        with col2:
            st.metric("Recent Research", f"{recent_papers}")
        with col3:
            coverage = (recent_papers / total_papers * 100) if total_papers > 0 else 0
            st.metric("Recent Coverage", f"{coverage:.1f}%")
        with col4:
            journals = len(set(p.get('journal', '') for p in papers))
            st.metric("Unique Journals", journals)
        
        # Research recommendations
        st.subheader("🎯 Recommended for Your Research")
        recommendations = [
            "🔬 CRISPR applications in your specific bioengineering field",
            "🧪 Latest protein engineering techniques for therapeutics", 
            "🦠 Emerging gene therapy delivery methods",
            "⚙️ Bioengineering approaches to regenerative medicine"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")

else:
    st.error("❌ No database connection. Please check your setup.")import streamlit as st
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
