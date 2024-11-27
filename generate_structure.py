import os

# Define the folder and file structure
structure = {
    "app": {
        "__init__.py": None,
        "main.py": None,
        "utils.py": None,
        "data": {
            "generate_embeddings.py": None,
        },
        "templates": {
            "index.html": None,
        },
        "static": {
            "css": {
                "styles.css": None,
            },
            "js": {
                "script.js": None,
            },
        },
    },
    "run.py": None,
    "requirements.txt": None,
    "README.md": None,
}

# Function to create the structure
def create_structure(base, structure):
    for name, content in structure.items():
        path = os.path.join(base, name)
        if isinstance(content, dict):  # If it's a nested structure (folder)
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)  # Recursively handle the nested structure
        else:  # If it's a file
            open(path, 'w').close()

# Base directory
base_dir = "wiley-ai-study-assistant"
os.makedirs(base_dir, exist_ok=True)

# Generate the structure
create_structure(base_dir, structure)
print("Project structure created successfully!")
