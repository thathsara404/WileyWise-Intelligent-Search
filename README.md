# Wiley AI Study Assistant

## Overview
This is an AI-powered study assistant that helps students ask questions, receive answers, and take quizzes based on Wiley Online Library content.

## Features
- Generate answers using GPT-4.
- Provide quizzes to reinforce learning.
- Use precomputed embeddings for semantic search.

## How to Run
1. Install dependencies: pip install -r requirements.txt
2. Create Open AI key and setup in utils file: https://platform.openai.com/api-keys
3. Generate embeddings: python app/data/generate_embeddings.py
4. Start the Flask server: python run.py
5. Open `http://127.0.0.1:5000` in your browser.

## Requirements
- Python 3.8+
- OpenAI API key


