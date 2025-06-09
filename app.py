# Research AI Web Interface
# Run with: streamlit run research_ai_app.py

import streamlit as st
import json
import pandas as pd
from datetime import datetime

import plotly.graph_objects as go
from ai_processor import ResearchKnowledgeBase, ResearchAI
import os

# Page config
st.set_page_config(
    page_title="Research AI Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .answer-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2e8b57;
    }
    .source-box {
        background-color: #fff;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_knowledge_base():
    """Load the knowledge base (cached for performance)"""
    if not os.path.exists('research_kb'):
        st.error("Knowledge base not found! Please run the AI processor first.")
        return None
    return ResearchKnowledgeBase()

@st.cache_resource
def load_ai_system(_kb):
    """Load the AI system (cached for performance)"""
    openai_key = st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, 'secrets') else None
    return ResearchAI(_kb, openai_key)

def display_source(source, index):
    """Display a research paper source"""
    with st.container():
        st.markdown(f"""
        <div class="source-box">
            <h4>📄 Source {index + 1}</h4>
            <p><strong>Title:</strong> {source['title']}</p>
            <p><strong>Authors:</strong> {source['authors'][:100]}...</p>
            <p><strong>Journal:</strong> {source['journal']} ({source['year']})</p>
            <p><strong>Relevance Score:</strong> {source['relevance_score']:.3f}</p>
            {f"<p><strong>PMID:</strong> {source['pmid']}</p>" if source['pmid'] else ""}
        </div>
        """, unsafe_allow_html=True)

def create_stats_dashboard(kb):
    """Create statistics dashboard"""
    stats = kb.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{stats['total_papers']:,}</h3>
            <p>Total Papers</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{stats['year_range']}</h3>
            <p>Year Range</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(stats['common_techniques'])}</h3>
            <p>Techniques Covered</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Active</h3>
            <p>AI Status</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🧬 Research AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown("*Your AI-powered research companion trained on thousands of scientific papers*")
    
    # Load systems
    kb = load_knowledge_base()
    if kb is None:
        st.stop()
    
    ai = load_ai_system(kb)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Stats
        st.subheader("📊 Database Stats")
        with st.expander("View Statistics"):
            create_stats_dashboard(kb)
        
        # Settings
        st.subheader("⚙️ Settings")
        max_sources = st.slider("Max sources per answer", 3, 15, 5)
        show_confidence = st.checkbox("Show confidence scores", True)
        
        # Recent questions
        st.subheader("🕒 Recent Questions")
        if 'recent_questions' not in st.session_state:
            st.session_state.recent_questions = []
        
        for i, q in enumerate(st.session_state.recent_questions[-5:]):
            if st.button(f"💭 {q[:30]}...", key=f"recent_{i}"):
                st.session_state.current_question = q
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Your Research Question")
        
        # Question input
        question = st.text_area(
            "What would you like to know?",
            placeholder="e.g., 'How can I optimize CRISPR efficiency in mammalian cells?' or 'What are the latest methods for protein purification?'",
            height=100,
            key="question_input"
        )
        
        # Example questions
        st.markdown("**💡 Example Questions:**")
        example_questions = [
            "How can I improve transfection efficiency in HEK293 cells?",
            "What are the best methods for CRISPR gene editing in vivo?",
            "How do I optimize protein expression in E. coli?",
            "What are recent advances in gene therapy delivery?",
            "How can I enhance cell reprogramming efficiency?",
            "What are the latest techniques for single-cell RNA sequencing?"
        ]
        
        col_ex1, col_ex2 = st.columns(2)
        for i, example in enumerate(example_questions):
            col = col_ex1 if i % 2 == 0 else col_ex2
            with col:
                if st.button(f"📝 {example[:40]}...", key=f"example_{i}"):
                    st.session_state.question_input = example
                    st.rerun()
        
        # Submit button
        if st.button("🔍 Search Research Literature", type="primary"):
            if question.strip():
                # Add to recent questions
                if question not in st.session_state.recent_questions:
                    st.session_state.recent_questions.append(question)
                
                # Show processing
                with st.spinner("🧠 Analyzing research literature..."):
                    result = ai.answer_research_question(question, max_papers=max_sources)
                
                # Display results
                st.markdown("---")
                st.markdown(f'<div class="question-box"><h3>❓ Your Question</h3><p>{question}</p></div>', unsafe_allow_html=True)
                
                # Answer
                st.markdown(f"""
                <div class="answer-box">
                    <h3>🤖 AI Research Summary</h3>
                    <p>{result['answer']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Confidence and metadata
                if show_confidence:
                    col_conf1, col_conf2, col_conf3 = st.columns(3)
                    with col_conf1:
                        st.metric("Confidence", f"{result['confidence']:.2f}")
                    with col_conf2:
                        st.metric("Sources Used", len(result['sources']))
                    with col_conf3:
                        st.metric("Papers Analyzed", result['context_papers'])
                
                # Sources
                if result['sources']:
                    st.markdown("### 📚 Source Papers")
                    
                    # Create tabs for sources
                    source_tabs = st.tabs([f"Source {i+1}" for i in range(len(result['sources']))])
                    
                    for i, (tab, source) in enumerate(zip(source_tabs, result['sources'])):
                        with tab:
                            display_source(source, i)
                
            else:
                st.warning("Please enter a research question!")
    
    with col2:
        st.header("📈 Research Insights")
        
        # Quick search
        st.subheader("🔎 Quick Paper Search")
        search_term = st.text_input("Search papers by keyword:")
        
        if search_term:
            papers = kb.search_papers(search_term, n_results=5)
            for i, paper in enumerate(papers):
                with st.expander(f"📄 {paper['metadata']['title'][:50]}..."):
                    st.write(f"**Authors:** {paper['metadata']['authors'][:100]}...")
                    st.write(f"**Journal:** {paper['metadata']['journal']} ({paper['metadata']['year']})")
                    st.write(f"**Relevance:** {1-paper['distance']:.3f}")
        
        # Research areas
        st.subheader("🧪 Popular Research Areas")
        research_areas = [
            ("CRISPR & Gene Editing", "🧬"),
            ("Protein Engineering", "🔬"),
            ("Cell Culture", "🦠"),
            ("Gene Therapy", "💉"),
            ("Synthetic Biology", "⚗️"),
            ("Regenerative Medicine", "🩹")
        ]
        
        for area, emoji in research_areas:
            if st.button(f"{emoji} {area}", key=f"area_{area}"):
                st.session_state.question_input = f"What are the latest advances in {area.lower()}?"
                st.rerun()
        
        # Tips
        st.subheader("💡 Research Tips")
        tips = [
            "Be specific in your questions for better results",
            "Ask about experimental procedures and protocols",
            "Include organism or cell type for targeted advice",
            "Ask for troubleshooting help with techniques",
            "Request comparisons between different methods"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")

if __name__ == "__main__":
    main()
