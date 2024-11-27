from sentence_transformers import SentenceTransformer
import pickle

# Load Sentence-BERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Example database of articles
database = [
    {
        "id": 1,
        "title": "Renewable Energy Benefits",
        "excerpt": "Renewable energy sources like wind and solar play a vital role in ensuring a sustainable future. They are cost-effective and significantly reduce carbon emissions, helping combat climate change and decrease reliance on fossil fuels. While renewable energy adoption leads to cleaner air, healthier ecosystems, and a stable climate, challenges such as energy storage and upfront investment costs must be addressed to fully harness their potential.",
        "link": "/articles/renewable-energy-benefits.html"
    },
    {
        "id": 2,
        "title": "Sustainable Agriculture",
        "excerpt": "Sustainable agriculture focuses on balancing food production with environmental preservation through practices like crop rotation, conservation tillage, and organic farming. These methods enhance soil health, conserve water, and reduce greenhouse gas emissions while promoting biodiversity, ecosystem stability, and social responsibility.",
        "link": "/articles/sustainable-agriculture.html"
    },
    {
        "id": 3,
        "title": "Understanding Cancers",
        "excerpt": "Cancer refers to a group of diseases involving the abnormal and uncontrolled growth of cells that can spread to other parts of the body. This complex condition affects millions globally and manifests in various forms, including breast, lung, prostate, colorectal, and skin cancers. The article delves into the causes of cancer, such as genetic mutations, environmental exposures, lifestyle factors, and infections like HPV and Hepatitis B. It highlights the importance of early detection through regular screenings, which can improve treatment outcomes and survival rates. Preventive measures, including a balanced diet, regular physical activity, avoiding tobacco and excessive alcohol consumption, and receiving vaccines against cancer-causing viruses, are strongly emphasized. The article also explores advancements in treatment options such as surgery, chemotherapy, radiation therapy, immunotherapy, and targeted therapies, showcasing how innovation is improving the quality of life for cancer patients. In addition, the psychological and social impacts of cancer, along with the importance of support systems, are discussed to provide a holistic view of the challenges faced by patients and their families. This comprehensive overview aims to raise awareness, promote prevention, and encourage a proactive approach to managing and combating cancer.",
        "link": "/articles/understanding-cancers.html"
    },
    {
        "id": 4,
        "title": "Global Economy Overview",
        "excerpt": "The global economy governs the production, distribution, and consumption of goods and services, involving individuals, businesses, and governments. Key elements like GDP, employment, inflation, and trade are interconnected and vital for stability. Growth depends on technology, investment, education, and sound policies, but challenges like inequality and external shocks pose risks. Emerging trends such as green energy, digital transformation, and globalization will shape the future, requiring collaboration and sustainable policies for equitable growth.",
        "link": "/articles/global-economy-overview.html"
    },
    # Add more articles as needed
]


# Generate embeddings for each article
for entry in database:
    entry["embedding"] = model.encode(entry["excerpt"])

# Save the database with embeddings
with open("app/data/database.pkl", "wb") as f:
    pickle.dump(database, f)

print("Embeddings generated and saved successfully!")
