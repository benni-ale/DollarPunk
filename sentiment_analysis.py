import json
import glob
import os
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

def load_finbert():
    """Load FinBERT model and tokenizer"""
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    return tokenizer, model

def get_sentiment(text, tokenizer, model):
    """Get sentiment scores for a text using FinBERT"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Get scores for positive, negative, neutral
    scores = predictions[0].detach().numpy()
    sentiment_dict = {
        "sentiment_positive": float(scores[0]),
        "sentiment_negative": float(scores[1]),
        "sentiment_neutral": float(scores[2]),
        "sentiment_label": ["positive", "negative", "neutral"][scores.argmax()]
    }
    return sentiment_dict

def process_json_file(file_path, tokenizer, model):
    """Process a single JSON file and add sentiment analysis"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Process each stock's news
    for ticker, news_list in tqdm(data['stocks'].items(), desc=f"Processing {os.path.basename(file_path)}"):
        for article in news_list:
            # Combine title and description for sentiment analysis
            text = f"{article['title']} {article['description']}"
            
            # Get sentiment scores
            sentiment = get_sentiment(text, tokenizer, model)
            
            # Add sentiment data to article
            article.update(sentiment)
    
    # Create new filename with _sentiment suffix
    base_path = os.path.splitext(file_path)[0]
    new_path = f"{base_path}_sentiment.json"
    
    # Save enriched data
    with open(new_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return new_path

def main():
    print("Loading FinBERT model...")
    tokenizer, model = load_finbert()
    
    # Find all JSON files in data directory
    json_files = glob.glob('data/*_news_*.json')
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process each file
    for file_path in json_files:
        if '_sentiment' not in file_path:  # Skip already processed files
            try:
                new_path = process_json_file(file_path, tokenizer, model)
                print(f"Processed {file_path} -> {new_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main() 