# import os
# import json
# import numpy as np
# from tqdm import tqdm
# import faiss
# from langchain_core.documents import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class DocumentProcessor:
#     def __init__(self, json_path, embeddings_dir="Embeddings"):
#         """
#         Initialize the DocumentProcessor with paths for the JSON file and FAISS index.
        
#         Args:
#             json_path: Path to the JSON file containing document text
#             embeddings_dir: Directory to store embeddings and indices
#         """
#         self.json_path = json_path
        
#         # Create base filename from original JSON name for the embedding folder
#         base_filename = os.path.splitext(os.path.basename(json_path))[0]
#         self.index_path = os.path.join(embeddings_dir, base_filename)
        
#         self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len,
#         )
        
#         # Create directories if they don't exist
#         os.makedirs(embeddings_dir, exist_ok=True)
#         os.makedirs(self.index_path, exist_ok=True)
    
#     def load_json_data(self):
#         """Load and parse the JSON file containing document text."""
#         try:
#             with open(self.json_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
            
#             # Combine all pages into one text document
#             all_text = ""
#             if isinstance(data, dict):
#                 for page_key, page_text in data.items():
#                     all_text += f"\n\n=== {page_key.upper()} ===\n\n"
#                     all_text += page_text
#                 return all_text
#             else:
#                 logger.warning("JSON structure isn't as expected. Using entire JSON content.")
#                 return json.dumps(data)
#         except Exception as e:
#             logger.error(f"Error loading JSON file: {e}")
#             raise
    
#     def process_documents(self):
#         """
#         Process JSON data into LangChain Document objects and split into chunks.
        
#         Returns:
#             List of Document objects
#         """
#         text_content = self.load_json_data()
        
#         # Create initial document
#         doc = Document(
#             page_content=text_content,
#             metadata={"source": self.json_path}
#         )
        
#         # Split document into chunks
#         docs = self.text_splitter.split_documents([doc])
#         logger.info(f"Split document into {len(docs)} chunks")
        
#         return docs
    
#     def create_faiss_index(self):
#         """
#         Create and save a FAISS index from document chunks.
        
#         Returns:
#             Tuple of (documents, FAISS index)
#         """
#         # Process documents into chunks
#         docs = self.process_documents()
        
#         # Generate embeddings
#         logger.info("Generating embeddings for document chunks...")
#         embeddings_list = []
#         for doc in tqdm(docs):
#             embedding = self.embeddings.embed_query(doc.page_content)
#             embeddings_list.append(embedding)
        
#         # Convert to numpy array for FAISS
#         embeddings_array = np.array(embeddings_list, dtype=np.float32)
        
#         # Create FAISS index
#         dimension = embeddings_array.shape[1]
#         index = faiss.IndexFlatL2(dimension)
#         index.add(embeddings_array)
        
#         # Save the index
#         faiss.write_index(index, os.path.join(self.index_path, "document.index"))
        
#         # Save documents to disk
#         with open(os.path.join(self.index_path, "documents.json"), "w", encoding="utf-8") as f:
#             json.dump([{"content": doc.page_content, "metadata": doc.metadata} for doc in docs], f, ensure_ascii=False)
        
#         logger.info(f"FAISS index created and saved at {self.index_path}")
        
#         return docs, index
    
#     def load_faiss_index(self):
#         """
#         Load the FAISS index and documents from disk.
        
#         Returns:
#             Tuple of (documents, FAISS index)
#         """
#         index_file = os.path.join(self.index_path, "document.index")
#         docs_file = os.path.join(self.index_path, "documents.json")
        
#         if not os.path.exists(index_file) or not os.path.exists(docs_file):
#             logger.info("FAISS index not found. Creating new index...")
#             return self.create_faiss_index()
        
#         # Load the index
#         index = faiss.read_index(index_file)
        
#         # Load documents
#         with open(docs_file, "r", encoding="utf-8") as f:
#             docs_data = json.load(f)
        
#         docs = [Document(page_content=item["content"], metadata=item["metadata"]) for item in docs_data]
        
#         logger.info(f"Loaded FAISS index with {len(docs)} documents")
        
#         return docs, index
    
#     def search_similar_documents(self, query, k=4):
#         """
#         Search for documents similar to the query.
        
#         Args:
#             query: Search query string
#             k: Number of similar documents to return
            
#         Returns:
#             List of similar Document objects
#         """
#         # Load documents and index
#         docs, index = self.load_faiss_index()
        
#         # Generate embedding for query
#         query_embedding = np.array([self.embeddings.embed_query(query)], dtype=np.float32)
        
#         # Search
#         D, I = index.search(query_embedding, k)
        
#         # Return matched documents
#         return [docs[i] for i in I[0]]

import os
import json
import numpy as np
from tqdm import tqdm
import faiss
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, json_path, embeddings_dir="Embeddings"):
        """
        Initialize the DocumentProcessor with paths for the JSON file and FAISS index.
        
        Args:
            json_path: Path to the JSON file containing document text
            embeddings_dir: Directory to store embeddings and indices
        """
        self.json_path = json_path
        base_filename = os.path.splitext(os.path.basename(json_path))[0]
        self.index_path = os.path.join(embeddings_dir, base_filename)
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Enhanced text splitter with logical separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Slightly smaller for better context handling
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ".", ","],
            length_function=len,
        )
        
        # Create directories if they don't exist
        os.makedirs(embeddings_dir, exist_ok=True)
        os.makedirs(self.index_path, exist_ok=True)

    def load_json_data(self):
        """Load and parse the JSON file containing structured document text."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            all_pages = []
            if isinstance(data, dict):
                for page_key, page_content in data.items():
                    page_number = data[page_key].get("page_number", None)
                    page_text = data[page_key].get("text", "")
                    all_pages.append({"page_number": page_number, "text": page_text})
            else:
                logger.warning("JSON structure unexpected. Using entire JSON content as one page.")
                all_pages = [{"page_number": 1, "text": json.dumps(data)}]

            return all_pages
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            raise

    def process_documents(self):
        """
        Process JSON data into LangChain Document objects and split into enriched chunks.
        
        Returns:
            List of Document objects with enhanced metadata.
        """
        pages = self.load_json_data()
        all_docs = []

        for page in pages:
            page_number = page["page_number"]
            page_text = page["text"]

            # Split page into chunks
            docs = self.text_splitter.create_documents(
                [page_text],
                metadatas=[{"source": self.json_path, "page_number": page_number}]
            )
            all_docs.extend(docs)

        logger.info(f"Split document into {len(all_docs)} enriched chunks with metadata.")
        return all_docs

    def create_faiss_index(self):
        """
        Create and save a FAISS index from document chunks.

        Returns:
            Tuple of (documents, FAISS index)
        """
        docs = self.process_documents()

        # Generate embeddings
        logger.info("Generating embeddings for document chunks...")
        embeddings_list = []
        for doc in tqdm(docs):
            embedding = self.embeddings.embed_query(doc.page_content)
            embeddings_list.append(embedding)

        embeddings_array = np.array(embeddings_list, dtype=np.float32)

        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)

        # Save the index and documents
        faiss.write_index(index, os.path.join(self.index_path, "document.index"))
        with open(os.path.join(self.index_path, "documents.json"), "w", encoding="utf-8") as f:
            json.dump([{"content": doc.page_content, "metadata": doc.metadata} for doc in docs], f, ensure_ascii=False)

        logger.info(f"FAISS index created and saved at {self.index_path}")
        return docs, index

    def load_faiss_index(self):
        """
        Load the FAISS index and documents from disk.

        Returns:
            Tuple of (documents, FAISS index)
        """
        index_file = os.path.join(self.index_path, "document.index")
        docs_file = os.path.join(self.index_path, "documents.json")

        if not os.path.exists(index_file) or not os.path.exists(docs_file):
            logger.info("FAISS index not found. Creating new index...")
            return self.create_faiss_index()

        index = faiss.read_index(index_file)
        with open(docs_file, "r", encoding="utf-8") as f:
            docs_data = json.load(f)

        docs = [Document(page_content=item["content"], metadata=item["metadata"]) for item in docs_data]

        logger.info(f"Loaded FAISS index with {len(docs)} documents")
        return docs, index

    def search_similar_documents(self, query, k=4):
        """
        Search for documents similar to the query.

        Args:
            query: Search query string
            k: Number of similar documents to return

        Returns:
            List of similar Document objects with metadata.
        """
        docs, index = self.load_faiss_index()

        query_embedding = np.array([self.embeddings.embed_query(query)], dtype=np.float32)

        D, I = index.search(query_embedding, k)

        return [docs[i] for i in I[0]]
