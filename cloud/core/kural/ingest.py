import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KURAL_Ingest")

# Paths
DATASET_PATH = "../../../Dataset/KURAL/train_dataset.xlsx" # Relative to cloud/core/kural
CHROMA_DB_DIR = "./chroma_db"

def ingest_data():
    logger.info("Loading Excel dataset...")
    # Adjust path to absolute for safety if run from different directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "../../../Dataset/KURAL/train_dataset.xlsx")
    
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found at {dataset_path}")
        return

    df = pd.read_excel(dataset_path)
    
    # We will combine question and answer for better semantic matching, or just search by question.
    # Let's search by question and store the answer in metadata so the LLM can use it.
    df['search_text'] = "Farmer Question: " + df['question'].astype(str)
    df['answer'] = df['answer'].astype(str)
    
    # Optional: Take a subset if the dataset is huge to avoid long embedding times initially
    # df = df.head(500) # Uncomment to test with 500 rows first
    
    logger.info(f"Loaded {len(df)} rows. Preparing documents...")
    loader = DataFrameLoader(df, page_content_column="search_text")
    documents = loader.load()

    logger.info("Initializing Multilingual Embeddings (this will download a model the first time)...")
    # Using a fast, lightweight multilingual model suitable for Indian & Global languages
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    logger.info("Creating Chroma Vector Store...")
    db_path = os.path.join(base_dir, "chroma_db")
    
    vectorstore = Chroma(
        persist_directory=db_path, 
        embedding_function=embeddings,
        collection_name="kural_knowledge"
    )
    
    batch_size = 5000
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        logger.info(f"Ingesting batch {i//batch_size + 1}/{(len(documents)//batch_size)+1}...")
        vectorstore.add_documents(batch)
    
    logger.info(f"Successfully ingested data into {db_path}!")

if __name__ == "__main__":
    ingest_data()
