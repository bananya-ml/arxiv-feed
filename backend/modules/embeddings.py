from sentence_transformers import SentenceTransformer
import hashlib
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import uuid

class EmbeddingsManager:
    def __init__(self, collection_name: str = "arxiv_papers", path: str = "./chroma_storage"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.chroma_client = chromadb.PersistentClient(path=path)
        self.collection_name = collection_name
        
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def generate_doc_id(self, url: str) -> str:
        """Generate a unique document ID based on URL"""
        content = f"{url}".encode('utf-8')
        return hashlib.sha256(content).hexdigest()

    def create_embeddings(self, text: str, url: str) -> List[Dict[str, Any]]:
        """Create embeddings for text chunks"""
        chunks = self.text_splitter.split_text(text)
        
        doc_id = self.generate_doc_id(url)
        
        embeddings = []
        for chunk in chunks:
            embedding = self.model.encode(chunk).tolist()
            embeddings.append({
                "doc_id": doc_id,
                "paper_url": url,
                "chunk_text": chunk,
                "embedding": embedding
            })
        
        return embeddings

    async def store_document_embeddings(self, text: str, url: str):
        """Store document embeddings in ChromaDB"""
        embeddings_data = self.create_embeddings(text, url)
        
        ids = [str(uuid.uuid4()) for _ in embeddings_data]
        embeddings = [data["embedding"] for data in embeddings_data]
        documents = [data["chunk_text"] for data in embeddings_data]
        metadatas = [
            {
                "doc_id": data["doc_id"],
                "paper_url": data["paper_url"]
            } 
            for data in embeddings_data
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search_similar_chunks(self, query: str, top_k: int = 5, url: str = "") -> List[Dict[str, Any]]:
        """Search for similar text chunks using the query"""

        query_embedding = self.model.encode(query).tolist()
        doc_id = self.generate_doc_id(url) if url else None

        filter = {"doc_id": doc_id} if doc_id else {}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )
        
        similar_chunks = []
        for i in range(len(results['ids'][0])):
            similar_chunks.append({
                "doc_id": results['metadatas'][0][i].get('doc_id', ''),
                "paper_url": results['metadatas'][0][i].get('paper_url', ''),
                "chunk_text": results['documents'][0][i],
                "distance": results['distances'][0][i]
            })
        
        return similar_chunks

# if __name__ == "__main__":
#     # Create an instance of EmbeddingsManager
#     manager = EmbeddingsManager()

#     sample_text = "This is a sample document text for generating embeddings."
#     sample_url = "http://example.com/sample-document"

#     # Store document embeddings
#     import asyncio
#     asyncio.run(manager.store_document_embeddings(sample_text, sample_url))

#     # Search for similar chunks
#     query = "sample document"
#     results = manager.search_similar_chunks(query, top_k=5, url=sample_url)
#     print("Search Results:")
#     for result in results:
#         print(result)