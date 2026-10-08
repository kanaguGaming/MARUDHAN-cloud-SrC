import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class KuralEngine:
    def __init__(self):
        # Initialize Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        # Load ChromaDB
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "chroma_db")
        
        self.vectorstore = Chroma(
            persist_directory=db_path, 
            embedding_function=self.embeddings,
            collection_name="kural_knowledge"
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Initialize Groq LLM (Ensure GROQ_API_KEY is in your environment variables)
        # Using llama3-70b-8192 for high quality and speed
        self.llm = ChatGroq(model="llama3-70b-8192", temperature=0.3)
        
        # Create Prompt Template
        system_prompt = """
        You are KURAL, an advanced multilingual AI assistant for the Marudhan agriculture system.
        You communicate with farmers to answer their agricultural queries based strictly on the provided context.
        If the answer is not in the context, say "I'm sorry, I don't have information on that specific topic in my agricultural knowledge base, but I can escalate this to a human expert."
        Always respond in the same language the farmer uses.
        
        Context from past expert answers:
        {context}
        
        Farmer's Question: {question}
        """
        self.prompt = ChatPromptTemplate.from_template(system_prompt)
        
        # Build RAG Chain
        def format_docs(docs):
            formatted = []
            for doc in docs:
                answer = doc.metadata.get('answer', 'No answer provided')
                formatted.append(f"Q: {doc.page_content}\nA: {answer}\n")
            return "\n".join(formatted)
            
        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query: str) -> str:
        """Process a query and return the AI's response."""
        try:
            response = self.chain.invoke(query)
            return response
        except Exception as e:
            return f"Error connecting to KURAL engine: {str(e)}"

# Singleton instance
kural = KuralEngine()

if __name__ == "__main__":
    # Test the engine locally
    import sys
    if not os.getenv("GROQ_API_KEY"):
        print("Please set GROQ_API_KEY environment variable.")
        sys.exit(1)
        
    print("KURAL Engine Initialized. Type 'quit' to exit.")
    while True:
        q = input("\nFarmer: ")
        if q.lower() == 'quit':
            break
        print(f"KURAL: {kural.ask(q)}")
