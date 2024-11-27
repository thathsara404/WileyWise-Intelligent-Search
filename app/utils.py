from openai import OpenAI
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import logging
import re
import io

# Sentence-BERT model
model = SentenceTransformer("all-MiniLM-L6-v2")
# OpenAI client (replace with your API key)
client = OpenAI(api_key="")

# In-memory cache to store embeddings and responses
cache = {}

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def normalize_text(text):
    """Normalize text by lowercasing and removing extra spaces and punctuation."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.strip()

def generate_embeddings(text):
    """Generate embeddings for a given text."""
    return model.encode(text)

def cache_response(question, embedding, answer, quiz, strictness):
    """Store the question, embedding, answer, and quiz in the cache."""
    # Combine normalized question and strictness as the cache key
    normalized_question = normalize_text(question)  # Normalize before caching
    cache_key = f"{normalized_question}::{strictness}"  # Use strictness as part of the key
    logging.info(f"Caching response for question: '{normalized_question}' with strictness: '{strictness}'")
    
    # Store the response in the cache
    cache[cache_key] = {
        "embedding": embedding,
        "answer": answer,
        "quiz": quiz,
        "strictness": strictness,
    }

def find_similar_question(query_embedding, strictness, threshold=0.9):
    """
    Check the cache for a similar question based on cosine similarity and strictness.
    Returns the cached question and response if a match is found.
    """
    for cache_key, data in cache.items():
        # Split the cache key into question and strictness
        cached_question, cached_strictness = cache_key.rsplit("::", 1)
        if cached_strictness != strictness:  # Skip entries with a different strictness
            continue

        cached_embedding = data["embedding"]
        similarity = 1 - cosine(query_embedding, cached_embedding)
        logging.info(f"Computed similarity with cached question '{cached_question}' (strictness: {cached_strictness}): {similarity}")

        if similarity >= threshold:
            logging.debug(f"Cache hit for question: '{cached_question}' with strictness: '{cached_strictness}' (similarity: {similarity})")
            return cached_question, data  # Return cached question and data
    logging.info("No matching question found in the cache.")
    return None, None  # No similar question found

def generate_answer_with_quiz(query, content, strictness):
    try:
        logging.info("Starting to generate an answer for the query.")
        logging.debug(f"Query: {query}")
        logging.debug(f"Content: {content[:100]}...")  # Log first 100 characters of content

        # Normalize query and generate embedding
        query = normalize_text(query)
        query_embedding = generate_embeddings(query)

        # Check the cache for similar questions
        cached_question, cached_data = find_similar_question(query_embedding, strictness)
        if cached_data:
            logging.info(f"Returning cached response for question: '{cached_question}'")
            return cached_data["answer"], cached_data["quiz"]

        # If no cached response, proceed to call OpenAI API
        logging.info("No cached response found. Generating a new response.")

        if strictness == "strict":
            prompt = (
                f"Provide a concise and accurate answer to the following question using only the information provided in the content. "
                f"If the content does not provide enough information to answer the question, respond with: "
                f"'Wiley Wise cannot provide a direct answer to this question. Please refer to the full article for more details or try Flexible strictness.' "
                f"Do not add any external information or assumptions.\n\n"
                f"Question: '{query}'\n\nContent: {content}"
            )
        else:  # Flexible
            prompt = (
                f"Provide a detailed and thoughtful answer to the following question using the content provided. "
                f"You may infer additional information if needed. "
                f"If the content does not provide enough information, respond with: "
                f"'Wiley Wise cannot provide a direct answer to this question. Please refer to the full article for more details.' "
                f"The answer should sound natural and self-contained.\n\n"
                f"Question: '{query}'\n\nContent: {content}"
            )

        # Generate an answer using the ChatCompletion API
        logging.info("Sending request to OpenAI ChatCompletion API for answer generation.")
        answer_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a highly precise AI assistant. Answer questions strictly based on the provided content without adding any information beyond the content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            stream=False,
        )

        # Extract the answer
        answer = answer_response.choices[0].message.content.strip()
        logging.info("Answer generation completed successfully.")
        logging.debug(f"Generated answer: {answer}")

        # Promote the full article
        answer += "\n\nThis appears to be a good fit for the content you’re looking for. Click the button bellow to explore the full article for more details."

        # Generate a quiz using the ChatCompletion API
        logging.info("Sending request to OpenAI ChatCompletion API for quiz generation.")
        quiz_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a highly precise AI assistant. Generate quiz questions strictly based on the provided content. "
                        "Do not include questions or answers that cannot be derived directly from the content. "
                        "If the content does not include enough information for a quiz, respond with: 'The content does not include sufficient information to generate a quiz.'"
                        "Format the output as a JSON object with the following structure:\n\n"
                        "{\n"
                        "  'questions': [\n"
                        "    {\n"
                        "      'type': 'True/False',\n"
                        "      'question': '...',\n"
                        "      'correct_answer': '...'\n"
                        "    },\n"
                        "    {\n"
                        "      'type': 'Multiple Choice',\n"
                        "      'question': '...',\n"
                        "      'options': ['a) ...', 'b) ...', 'c) ...', 'd) ...'],\n"
                        "      'correct_answer': '...'\n"
                        "    },\n"
                        "    {\n"
                        "      'type': 'Fill in the Blank',\n"
                        "      'question': '...',\n"
                        "      'correct_answer': '...'\n"
                        "    }\n"
                        "  ]\n"
                        "}\n\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Using ONLY the following text, generate three quiz questions with answers. "
                        "Ensure that all questions and answers are strictly based on the provided text. "
                        "Include one true/false question, one multiple-choice question (with four options), and one fill-in-the-blank question. "
                        "Ensure each question tests a different aspect of the content.\n\n"
                        f"Content: {content}"
                    ),
                },
            ],
            max_tokens=400,
            stream=False,
        )

        # Extract the quiz
        quiz = quiz_response.choices[0].message.content.strip()
        logging.info("Quiz generation completed successfully.")
        logging.debug(f"Generated quiz: {quiz}")

        # Cache the response
        cache_response(query, query_embedding, answer, quiz, strictness)

        return answer, quiz
    except Exception as e:
        logging.error("An error occurred during answer or quiz generation.", exc_info=True)
        return f"Error generating response: {e}", ""
    
def find_relevant_content(query, database):
    """
    Finds the most relevant content from the database for a given query using cosine similarity.
    Args:
        query (str): The user's query.
        database (list): A list of dictionary entries, each with an "embedding" field.

    Returns:
        str: The excerpt of the most relevant content or a "not found" message.
    """
    logging.info("Starting to find relevant content for the query.")
    logging.debug(f"Query: {query}")
    
    # Generate query embedding
    logging.info("Generating embedding for the query.")
    query_embedding = model.encode(query)
    logging.debug(f"Query embedding: {query_embedding}")

    best_match = None
    highest_similarity = 0.4

    # Find best matching entry
    logging.info("Iterating through the database to find the best match.")
    for idx, entry in enumerate(database):
        logging.debug(f"Processing entry {idx + 1}/{len(database)}: {entry.get('title', 'No Title')}")
        similarity = 1 - cosine(query_embedding, entry["embedding"])
        logging.debug(f"Computed similarity: {similarity} for entry: {entry.get('title', 'No Title')}")

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = entry
            logging.debug(f"New best match found with similarity: {highest_similarity}")

    if best_match:
        logging.info(f"Best match found with similarity: {highest_similarity}")
        logging.debug(f"Best match details: {best_match}")
        return {
            "excerpt": best_match["excerpt"],
            "link": best_match["link"]
        }
    else:
        logging.warning("No relevant content found in the database.")
        return {
            "excerpt": "No relevant content found.",
            "link": None
        }

def transcribe_audio_util(file_storage, language="en"):
    """
    Transcribes an audio file using OpenAI's Whisper API.
    
    Args:
        audio_file: File-like object of the audio to transcribe.
        language: The language of the audio for transcription (default is 'en').

    Returns:
        dict: Transcription result from OpenAI API.
    """
    try:
        logging.info("Sending audio file for transcription.")

        audio_bytes = file_storage.read()
        audio_file = io.BytesIO(audio_bytes)  # Create a file-like object from bytes
        audio_file.name = file_storage.filename  # Set a name attribute for compatibility

        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language
        )
        logging.info("Transcription successful.")
         # Ensure response is a dictionary
        return response if isinstance(response, dict) else response.to_dict()
    except Exception as e:
        logging.error("Error during transcription.", exc_info=True)
        raise e
