# Simple Paper Collection Script
import requests
import json
import time
from supabase import create_client
import os

# Your Supabase credentials
SUPABASE_URL = "https://qqfsxntyinanhutdznts.supabase.co"  # Replace with yours
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxZnN4bnR5aW5hbmh1dGR6bnRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzNjA0MzAsImV4cCI6MjA2NDkzNjQzMH0.zN803irtPItd1Gcob7Q5XI5BSLg_ktfGu23MpIrLznc"  # Replace with yours

def collect_papers():
    print("🧬 Starting paper collection...")
    
    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Simple test - add a few sample papers
    sample_papers = [
        {
            "title": "CRISPR gene editing advances in 2024",
            "abstract": "Recent developments in CRISPR technology show improved efficiency...",
            "authors": "Smith J, Johnson A",
            "journal": "Nature Biotechnology",
            "year": 2024,
            "pmid": "12345678"
        },
        {
            "title": "Protein engineering for therapeutics",
            "abstract": "Novel approaches to protein design enable better drug development...",
            "authors": "Brown M, Davis K",
            "journal": "Science",
            "year": 2024,
            "pmid": "87654321"
        }
    ]
    
    # Add to database
    for paper in sample_papers:
        try:
            result = supabase.table('papers').insert(paper).execute()
            print(f"✅ Added: {paper['title'][:50]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("🎉 Sample papers added!")

if __name__ == "__main__":
    collect_papers()
