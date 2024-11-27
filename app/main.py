from flask import Flask, render_template, send_from_directory, request, jsonify, abort, session, redirect, url_for
from app.utils import find_relevant_content, generate_answer_with_quiz, transcribe_audio_util
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key for session management

# In-memory user data with saved conversations
user_data = {
    "user1": {"name": "User One", "password": "password1", "saved_conversations": []},
    "user2": {"name": "User Two","password": "password2", "saved_conversations": []},
}

# Load precomputed database
import pickle
with open("app/data/database.pkl", "rb") as f:
    database = pickle.load(f)

@app.route('/')
def home():
    # Redirect to login page if not logged in
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in user_data and user_data[username]["password"] == password:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/save_conversation", methods=["POST"])
def save_conversation():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    username = session["username"]
    data = request.json
    query = data.get("query")
    answer = data.get("answer")
    quiz = data.get("quiz")
    strictness = data.get("strictness")
    link = data.get("link")

    if not query or not answer:
        return jsonify({"error": "Invalid data"}), 400

    # Check for duplicates
    saved_conversations = user_data[username]["saved_conversations"]
    for conversation in saved_conversations:
        if conversation["query"] == query and conversation["strictness"] == strictness:
            return jsonify({"error": "Conversation already exists"}), 400

    # Save the conversation
    saved_conversations.append({"query": query, "answer": answer, "quiz": quiz, "strictness": strictness, "link": link})
    return jsonify({"message": "Conversation saved successfully"}), 200

@app.route("/get_saved_conversations", methods=["GET"])
def get_saved_conversations():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    username = session["username"]
    return jsonify(user_data[username]["saved_conversations"])  # Return saved conversations as JSON


@app.route("/get_user_details", methods=["GET"])
def get_user_details():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    username = session["username"]
    # Retrieve user details
    user_details = {
        "username": username,
        "name": user_data[username].get("name", "Unknown"),
        "saved_conversations_count": len(user_data[username]["saved_conversations"])
    }
    # Return as JSON object
    return jsonify(user_details)

@app.route("/delete_conversation", methods=["POST"])
def delete_conversation():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    username = session["username"]
    data = request.json
    query = data.get("query")
    strictness = data.get("strictness")

    # Validate input
    if not query or not strictness:
        return jsonify({"error": "Invalid data"}), 400

    saved_conversations = user_data[username]["saved_conversations"]

    # Filter out the conversation to delete
    user_data[username]["saved_conversations"] = [
        c for c in saved_conversations if not (c["query"] == query and c["strictness"] == strictness)
    ]
    return jsonify({"message": "Conversation deleted successfully"}), 200


@app.route('/logout')
def logout():
    session.clear()  # Clear session
    return redirect(url_for('login'))

# Serve articles from the 'articles' directory
@app.route('/articles/<path:filename>')
def serve_article(filename):
    try:
        return send_from_directory('articles', filename)
    except FileNotFoundError:
        abort(404)

@app.route('/ask', methods=['POST'])
def ask():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401  # Unauthorized if not logged in

    data = request.json
    query = data.get("query", "")
    strictness = data.get('strictness')
    if not query:
        return jsonify({"error": "No query provided."}), 400

    # Find relevant content and its link
    relevant_content = find_relevant_content(query, database)
    excerpt = relevant_content["excerpt"]
    link = relevant_content["link"]

    if excerpt != "No relevant content found.":
        # Generate answer and quiz
        answer, quiz = generate_answer_with_quiz(query, excerpt, strictness)
        response = {
            "answer": answer,
            "quiz": quiz,
            "link": link
        }
    else:
        response = {
            "error": "No relevant content found in Wiley library.",
            "link": None
        }

    return jsonify(response)

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        if not session.get('logged_in'):
            return jsonify({"error": "Unauthorized"}), 401  # Unauthorized if not logged in

        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        audio_file = request.files["file"]  # Get the FileStorage object
        language = request.form.get("language", "en")  # Default language is English

        # Call the transcription utility function
        transcription = transcribe_audio_util(audio_file, language)

        # Return the transcription as JSON
        return jsonify(transcription), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
