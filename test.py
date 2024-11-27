from transformers import pipeline

# Load a pre-trained question-answering pipeline
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Define the question and context
question = "can we use wind as a renewable energy source?"
context = "Renewable energy sources like wind and solar play a vital role in ensuring a sustainable future. They are cost-effective and significantly reduce carbon emissions, helping combat climate change and decrease reliance on fossil fuels."

# Get the result from the pipeline
result = qa_pipeline({
    "question": question,
    "context": context
})

# Adjust confidence threshold or split the context
if result['score'] < 0.8:  # Adjust threshold
    print("The context might not provide a fully reliable answer to the question, but here's the result:")
    print(f"Answer: {result['answer']}")
else:
    print(f"Answer: {result['answer']}")
