import streamlit as st
import os
from supabase import create_client

# Page config
st.set_page_config(
    page_title="Research AI Assistant",
    page_icon="🧬",
    layout="wide"
)

# Initialize Supabase connection
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    
    if not url or not key:
        st.error("Please set up your Supabase credentials in Streamlit secrets!")
        return None
    
    return create_client(url, key)

def search_papers(supabase, query, limit=5):
    """Search papers by title/abstract"""
    try:
        # Simple text search in title and abstract
        result = supabase.table('papers').select('*').ilike('title', f'%{query}%').limit(limit).execute()
        papers = result.data or []
        
        # If no title matches, try abstract
        if not papers:
            result = supabase.table('papers').select('*').ilike('abstract', f'%{query}%').limit(limit).execute()
            papers = result.data or []
        
        return papers
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

def generate_answer(papers, question):
    """Generate answer from found papers"""
    if not papers:
        return "No relevant papers found. Try different keywords like 'CRISPR', 'protein', or 'gene'."
    
    answer = f"Based on {len(papers)} research papers:\n\n"
    
    for i, paper in enumerate(papers, 1):
        answer += f"**{i}. {paper['title']}**\n"
        answer += f"   - Authors: {paper['authors']}\n"
        answer += f"   - Journal: {paper['journal']} ({paper['year']})\n"
        if paper['abstract']:
            answer += f"   - Summary: {paper['abstract'][:200]}...\n"
        answer += "\n"
    
    answer += f"💡 These papers suggest various approaches to your question about {question.lower()}. "
    answer += "For detailed protocols, refer to the full papers."
    
    return answer

def main():
    # Header
    st.title("🧬 Research AI Assistant")
    st.markdown("*Your AI research companion*")
    
    # Initialize Supabase
    supabase = init_supabase()
    if not supabase:
        st.stop()
    
    # Check database connection
    try:
        result = supabase.table('papers').select('id').limit(1).execute()
        paper_count = len(supabase.table('papers').select('id').execute().data or [])
        st.success(f"✅ Connected! Database has {paper_count} papers")
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()
    
    # Main interface
    st.header("💬 Ask Your Research Question")
    
    question = st.text_area(
        "What would you like to know?",
        placeholder="e.g., 'Tell me about CRISPR gene editing' or 'What are protein engineering methods?'",
        height=100
    )
    
    if st.button("🔍 Search Research Literature", type="primary"):
        if question.strip():
            with st.spinner("🧠 Searching research papers..."):
                # Extract key terms for search
                search_terms = question.lower().split()
                search_query = " ".join([term for term in search_terms if len(term) > 3])[:50]
                
                # Search papers
                papers = search_papers(supabase, search_query)
                
                # Generate answer
                answer = generate_answer(papers, question)
                
                # Display results
                st.markdown("---")
                st.markdown(f"**❓ Your Question:** {question}")
                st.markdown("**🤖 AI Answer:**")
                st.markdown(answer)
                
                if papers:
                    st.markdown("**📚 Source Papers:**")
                    for paper in papers:
                        with st.expander(f"📄 {paper['title'][:60]}..."):
                            st.write(f"**Authors:** {paper['authors']}")
                            st.write(f"**Journal:** {paper['journal']} ({paper['year']})")
                            st.write(f"**PMID:** {paper.get('pmid', 'N/A')}")
                            if paper['abstract']:
                                st.write(f"**Abstract:** {paper['abstract']}")
        else:
            st.warning("Please enter a research question!")
    
    # Sidebar with stats
    with st.sidebar:
        st.header("📊 Database Stats")
        try:
            total_papers = len(supabase.table('papers').select('id').execute().data or [])
            recent_papers = len(supabase.table('papers').select('id').gte('year', 2020).execute().data or [])
            
            st.metric("Total Papers", total_papers)
            st.metric("Recent Papers (2020+)", recent_papers)
        except:
            st.write("Stats unavailable")
        
        st.header("💡 Try These Questions")
        example_questions = [
            "What is CRISPR gene editing?",
            "How does protein engineering work?",
            "What are gene therapy methods?",
            "Tell me about synthetic biology"
        ]
        
        for q in example_questions:
            if st.button(f"💭 {q}", key=f"example_{q[:20]}"):
                st.session_state.question = q

if __name__ == "__main__":
    main()
