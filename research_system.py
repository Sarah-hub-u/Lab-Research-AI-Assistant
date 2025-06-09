# 100% Free Cloud Research AI System
# No credit cards, no trials, completely free forever

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import requests
import weaviate
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from typing import List, Dict, Any
import logging

# Free services configuration
class FreeCloudConfig:
    """Configuration for free cloud services"""
    
    # Supabase (Free PostgreSQL)
    SUPABASE_URL = os.getenv('SUPABASE_URL')  # From Supabase dashboard
    SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')  # From Supabase dashboard
    
    # Weaviate Cloud (Free vector database)
    WEAVIATE_URL = os.getenv('WEAVIATE_URL')  # From Weaviate console
    WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')  # From Weaviate console
    
    # Email for PubMed (required for API access)
    PUBMED_EMAIL = os.getenv('PUBMED_EMAIL', 'your-email@university.edu')

class SupabaseStorage:
    """Free PostgreSQL storage using Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            FreeCloudConfig.SUPABASE_URL,
            FreeCloudConfig.SUPABASE_KEY
        )
        self.setup_tables()
    
    def setup_tables(self):
        """Create tables if they don't exist"""
        # Note: You can also create these in Supabase dashboard GUI
        create_papers_table = """
        CREATE TABLE IF NOT EXISTS papers (
            id SERIAL PRIMARY KEY,
            pmid VARCHAR(20) UNIQUE,
            doi VARCHAR(200),
            title TEXT,
            abstract TEXT,
            authors TEXT,
            journal VARCHAR(500),
            year INTEGER,
            keywords TEXT,
            source VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            processed BOOLEAN DEFAULT FALSE
        );
        """
        
        # Execute via Supabase SQL editor or API
        # This is handled in Supabase dashboard for simplicity
        pass
    
    def add_papers(self, papers: List[Dict]):
        """Add papers to Supabase"""
        processed_papers = []
        
        for paper in papers:
            processed_paper = {
                'pmid': paper.get('pmid'),
                'doi': paper.get('doi'),
                'title': paper.get('title'),
                'abstract': paper.get('abstract'),
                'authors': ', '.join(paper.get('authors', [])) if paper.get('authors') else None,
                'journal': paper.get('journal'),
                'year': int(paper.get('year')) if str(paper.get('year', '')).isdigit() else None,
                'keywords': ', '.join(paper.get('keywords', [])) if paper.get('keywords') else None,
                'source': paper.get('source', 'pubmed'),
                'processed': False
            }
            processed_papers.append(processed_paper)
        
        # Insert to Supabase (handles duplicates gracefully)
        try:
            result = self.supabase.table('papers').upsert(
                processed_papers, 
                on_conflict='pmid'
            ).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            st.error(f"Error adding papers: {e}")
            return 0
    
    def get_unprocessed_papers(self, limit: int = 100):
        """Get papers that need processing"""
        result = self.supabase.table('papers').select('*').eq('processed', False).limit(limit).execute()
        return result.data if result.data else []
    
    def mark_as_processed(self, paper_ids: List[int]):
        """Mark papers as processed"""
        for paper_id in paper_ids:
            self.supabase.table('papers').update({'processed': True}).eq('id', paper_id).execute()
    
    def get_paper_by_id(self, paper_id: int):
        """Get specific paper"""
        result = self.supabase.table('papers').select('*').eq('id', paper_id).execute()
        return result.data[0] if result.data else None
    
    def search_papers_text(self, query: str, limit: int = 10):
        """Text-based search in papers"""
        # Supabase supports full-text search
        result = self.supabase.table('papers').select('*').text_search(
            'title', query
        ).limit(limit).execute()
        return result.data if result.data else []
    
    def get_stats(self):
        """Get database statistics"""
        total_result = self.supabase.table('papers').select('id', count='exact').execute()
        processed_result = self.supabase.table('papers').select('id', count='exact').eq('processed', True).execute()
        
        total = total_result.count if hasattr(total_result, 'count') else 0
        processed = processed_result.count if hasattr(processed_result, 'count') else 0
        
        return {
            'total_papers': total,
            'processed_papers': processed,
            'processing_progress': f"{(processed/total*100):.1f}%" if total > 0 else "0%"
        }

class WeaviateVectorStorage:
    """Free vector storage using Weaviate Cloud"""
    
    def __init__(self):
        # Connect to Weaviate Cloud (free tier)
        self.client = weaviate.Client(
            url=FreeCloudConfig.WEAVIATE_URL,
            auth_client_secret=weaviate.AuthApiKey(api_key=FreeCloudConfig.WEAVIATE_API_KEY)
        )
        
        self.encoder = SentenceTransformer('allenai/scibert_scivocab_uncased')
        self.class_name = "ResearchPaper"
        self.setup_schema()
    
    def setup_schema(self):
        """Create Weaviate schema for research papers"""
        schema = {
            "class": self.class_name,
            "description": "Research papers with semantic search",
            "vectorizer": "none",  # We'll provide our own vectors
            "properties": [
                {
                    "name": "paper_id",
                    "dataType": ["int"],
                    "description": "Database paper ID"
                },
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Paper title"
                },
                {
                    "name": "abstract",
                    "dataType": ["text"],
                    "description": "Paper abstract"
                },
                {
                    "name": "authors",
                    "dataType": ["text"], 
                    "description": "Paper authors"
                },
                {
                    "name": "journal",
                    "dataType": ["text"],
                    "description": "Journal name"
                },
                {
                    "name": "year",
                    "dataType": ["int"],
                    "description": "Publication year"
                },
                {
                    "name": "relevance_score",
                    "dataType": ["number"],
                    "description": "Relevance score for queries"
                }
            ]
        }
        
        # Create class if it doesn't exist
        if not self.client.schema.exists(self.class_name):
            self.client.schema.create_class(schema)
    
    def add_papers(self, papers: List[Dict]):
        """Add papers with embeddings to Weaviate"""
        
        with self.client.batch as batch:
            for paper in papers:
                # Create document text for embedding
                doc_text = f"""
                Title: {paper.get('title', '')}
                Abstract: {paper.get('abstract', '')}
                Authors: {paper.get('authors', '')}
                Keywords: {paper.get('keywords', '')}
                """.strip()
                
                # Create embedding
                embedding = self.encoder.encode(doc_text).tolist()
                
                # Prepare properties
                properties = {
                    "paper_id": paper.get('id'),
                    "title": paper.get('title', ''),
                    "abstract": paper.get('abstract', '')[:1000],  # Limit length
                    "authors": paper.get('authors', ''),
                    "journal": paper.get('journal', ''),
                    "year": paper.get('year') or 0,
                    "relevance_score": 1.0
                }
                
                # Add to batch
                batch.add_data_object(
                    data_object=properties,
                    class_name=self.class_name,
                    vector=embedding
                )
    
    def search_papers(self, query: str, limit: int = 10):
        """Semantic search for papers"""
        # Create query embedding
        query_embedding = self.encoder.encode(query).tolist()
        
        # Search in Weaviate
        result = (
            self.client.query
            .get(self.class_name, ["paper_id", "title", "authors", "journal", "year"])
            .with_near_vector({"vector": query_embedding})
            .with_limit(limit)
            .with_additional(["distance"])
            .do()
        )
        
        papers = result.get('data', {}).get('Get', {}).get(self.class_name, [])
        
        # Convert to consistent format
        formatted_papers = []
        for paper in papers:
            formatted_papers.append({
                'paper_id': paper.get('paper_id'),
                'title': paper.get('title'),
                'authors': paper.get('authors'),
                'journal': paper.get('journal'),
                'year': paper.get('year'),
                'distance': paper.get('_additional', {}).get('distance', 1.0),
                'relevance_score': 1 - paper.get('_additional', {}).get('distance', 1.0)
            })
        
        return formatted_papers

class FreeResearchAI:
    """Complete research AI using only free services"""
    
    def __init__(self):
        self.paper_storage = SupabaseStorage()
        self.vector_storage = WeaviateVectorStorage()
    
    def collect_papers_from_pubmed(self, queries: List[str], papers_per_query: int = 500):
        """Collect papers from PubMed API (free)"""
        from src.data_collection.pubmed_scraper import PubMedScraper
        
        scraper = PubMedScraper()
        all_papers = []
        
        for query in queries:
            st.info(f"Collecting papers for: {query}")
            
            # Search for paper IDs
            pmid_list = scraper.search_papers(query, max_results=papers_per_query)
            
            if pmid_list:
                # Get paper details
                papers = scraper.fetch_paper_details(pmid_list)
                all_papers.extend(papers)
                
                st.success(f"Collected {len(papers)} papers for '{query}'")
        
        # Add to database
        if all_papers:
            added_count = self.paper_storage.add_papers(all_papers)
            st.success(f"Added {added_count} new papers to database!")
        
        return all_papers
    
    def process_papers_for_ai(self):
        """Process unprocessed papers for AI search"""
        # Get papers that need processing
        papers = self.paper_storage.get_unprocessed_papers(100)
        
        if not papers:
            st.info("No papers to process!")
            return
        
        st.info(f"Processing {len(papers)} papers for AI search...")
        
        # Add to vector database
        self.vector_storage.add_papers(papers)
        
        # Mark as processed
        paper_ids = [p['id'] for p in papers]
        self.paper_storage.mark_as_processed(paper_ids)
        
        st.success(f"Successfully processed {len(papers)} papers!")
    
    def answer_research_question(self, question: str, max_papers: int = 5):
        """Answer research question using AI"""
        
        # Search for relevant papers
        relevant_papers = self.vector_storage.search_papers(question, limit=max_papers)
        
        if not relevant_papers:
            return {
                'answer': "No relevant papers found. Try different keywords or collect more papers.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Get full paper details
        sources = []
        for paper in relevant_papers:
            full_paper = self.paper_storage.get_paper_by_id(paper['paper_id'])
            if full_paper:
                sources.append({
                    'title': full_paper['title'],
                    'authors': full_paper['authors'],
                    'journal': full_paper['journal'],
                    'year': full_paper['year'],
                    'abstract': full_paper['abstract'][:300] + "..." if full_paper['abstract'] else "",
                    'pmid': full_paper['pmid'],
                    'relevance_score': paper['relevance_score']
                })
        
        # Generate answer (simple version)
        answer = self._generate_simple_answer(question, sources)
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': min(0.9, len(sources) * 0.15),
            'papers_analyzed': len(sources)
        }
    
    def _generate_simple_answer(self, question: str, sources: List[Dict]) -> str:
        """Generate answer from sources"""
        if not sources:
            return "No relevant research found."
        
        answer = f"Based on {len(sources)} recent research papers:\n\n"
        
        # Extract insights
        recent_years = [s['year'] for s in sources if s['year'] and s['year'] > 2020]
        if recent_years:
            answer += f"Recent studies ({min(recent_years)}-{max(recent_years)}) show:\n\n"
        
        # Top findings
        for i, source in enumerate(sources[:3], 1):
            title = source['title'][:80] + "..." if len(source['title']) > 80 else source['title']
            answer += f"{i}. **{title}**\n"
            answer += f"   - Journal: {source['journal']} ({source['year']})\n"
            answer += f"   - Relevance: {source['relevance_score']:.2f}\n\n"
        
        answer += f"💡 **Key Insights**: These {len(sources)} papers suggest multiple approaches to your question. "
        answer += "For detailed protocols and methodologies, refer to the full papers cited above.\n\n"
        answer += f"🔬 **Next Steps**: Consider reviewing the highest-relevance papers for specific experimental details."
        
        return answer
    
    def get_system_status(self):
        """Get overall system status"""
        paper_stats = self.paper_storage.get_stats()
        
        return {
            'status': '✅ Online',
            'database': 'Supabase (Free)',
            'vector_search': 'Weaviate (Free)',
            'total_papers': paper_stats['total_papers'],
            'processed_papers': paper_stats['processed_papers'],
            'processing_progress': paper_stats['processing_progress'],
            'cost': '$0.00/month',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Environment setup for free services
FREE_SETUP_GUIDE = """
# Free Cloud Services Setup (No Credit Card Required)

## 1. Supabase (Free PostgreSQL Database)
1. Go to supabase.com
2. Sign up with GitHub (free)
3. Create new project
4. Get URL and anon key from Settings > API
5. Create papers table in SQL Editor

## 2. Weaviate Cloud (Free Vector Database) 
1. Go to console.weaviate.cloud
2. Sign up (free tier = 1M vectors)
3. Create new cluster
4. Get URL and API key from cluster details

## 3. Streamlit Community Cloud (Free Hosting)
1. Go to streamlit.io/cloud
2. Connect GitHub account
3. Deploy directly from GitHub repo
4. Get your free URL: yourapp.streamlit.app

## 4. Environment Variables (.env file)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key
PUBMED_EMAIL=your-email@university.edu
```

Total Cost: $0.00/month forever! 🎉
"""

if __name__ == "__main__":
    print("🆓 Free Cloud Research AI System")
    print("=" * 40)
    print(FREE_SETUP_GUIDE)
