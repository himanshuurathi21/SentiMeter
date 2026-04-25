import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_sentiment_model():
    """Downloads and caches the model so it only runs once."""
    model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model=model_path, 
        tokenizer=model_path,
        return_all_scores=True
    )
    return sentiment_pipeline

def process_results(results):
    """Formats the raw AI data into a clean list for the UI."""
    mapping = {"negative": "Negative", "neutral": "Neutral", "positive": "Positive"}
    formatted_data = []
    
    if not results:
        return []

    # Handle different list formats from Hugging Face
    actual_results = results[0] if isinstance(results[0], list) else results
    
    for res in actual_results:
        label_key = res['label'].lower()
        formatted_data.append({
            "Label": mapping.get(label_key, label_key.capitalize()),
            "Score": round(res['score'] * 100, 2)
        })
    return formatted_data