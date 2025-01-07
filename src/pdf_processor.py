from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from typing import List, Dict
import pypdf

def extract_metadata_from_pdf(file_path: str) -> Dict:
    """Extract metadata from PDF properties/metadata fields"""
    metadata = {}
    try:
        with open(file_path, 'rb') as file:
            pdf = pypdf.PdfReader(file)
            if pdf.metadata and pdf.metadata.get('/Keywords'):
                keywords = pdf.metadata.get('/Keywords')
                print(f"Found keywords: {keywords}")
                
                for item in keywords.split(';'):
                    item = item.strip()
                    if ':' in item:
                        key, value = item.split(':', 1)
                        metadata[key.strip()] = value.strip()
                        
                print(f"Extracted metadata: {metadata}")
            else:
                print("No Keywords metadata found in PDF")
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    
    return metadata

def process_document_with_chunking(file_path: str) -> List[Dict]:
    """Process PDF with chunking"""
    # Load PDF
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Initialize text splitter for chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10,
        chunk_overlap=2,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Split into chunks
    chunks = text_splitter.split_documents(pages)
    
    # Extract metadata
    metadata = extract_metadata_from_pdf(file_path)
    
    # Process each chunk with metadata
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            'chunk_id': i,
            'total_chunks': len(chunks),
            'source': os.path.basename(file_path)
        })
        
        processed_chunks.append({
            'content': chunk.page_content,
            'metadata': chunk_metadata
        })
    
    return processed_chunks

def load_pdfs_from_directory(directory: str = "./data") -> List[Dict]:
    """Load PDFs with chunking"""
    documents = []
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    
    print(f"\nFound PDF files: {pdf_files}")
    
    for pdf_file in pdf_files:
        file_path = os.path.join(directory, pdf_file)
        try:
            print(f"\nProcessing: {pdf_file}")
            
            # Process document with chunking
            chunks = process_document_with_chunking(file_path)
            
            # Validate and add chunks
            for chunk in chunks:
                metadata = chunk['metadata']
                if all(key in metadata for key in ['date', 'version', 'security']):
                    documents.append(chunk)
                    print(f"Successfully loaded chunk {metadata['chunk_id']} from {pdf_file}")
                else:
                    print(f"Warning: Incomplete metadata in chunk from {pdf_file}")
                    print("Current metadata:", metadata)
                
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
    
    return documents