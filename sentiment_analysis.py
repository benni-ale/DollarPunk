import json
import glob
import os
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm
from simple_logger import logger

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

def process_json_file(input_file, tokenizer, model):
    """
    Process a JSON file containing news articles and add sentiment analysis
    """
    # Log start of execution
    logger.log_execution("sentiment_analysis.py", "started", {
        "function": "process_json_file",
        "input_file": input_file
    })
    
    try:
        # Load the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_sentiment.json"
        
        # Process each stock's articles
        total_articles = 0
        processed_articles = 0
        
        for ticker, articles in data.get('stocks', {}).items():
            total_articles += len(articles)
            for article in articles:
                if 'title' in article and article['title']:
                    # Analyze title sentiment
                    sentiment_dict = get_sentiment(article['title'], tokenizer, model)
                    article.update(sentiment_dict)
                    processed_articles += 1
        
        # Save the processed data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Log successful completion
        logger.log_execution("sentiment_analysis.py", "completed", {
            "input_file": input_file,
            "output_file": output_file,
            "total_articles": total_articles,
            "processed_articles": processed_articles
        })
        
        return output_file
        
    except Exception as e:
        # Log error
        logger.log_execution("sentiment_analysis.py", "failed", {
            "input_file": input_file,
            "error": str(e)
        })
        raise e

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