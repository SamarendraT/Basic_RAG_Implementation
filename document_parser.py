import os
from pathlib import Path
from typing import List, Tuple
import PyPDF2
from docx import Document as DocxDocument
import re


class TextChunker:
    """Split text into context-relevant chunks."""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks while respecting sentence boundaries.
        
        Args:
            text: The text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence exceeds chunk_size, save current chunk and start new one
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from the end of current chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks


class DocumentParser:
    """Parse multiple document types and extract text."""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF files."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Extract text from DOCX files."""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Extract text from TXT files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")
    
    @staticmethod
    def parse_document(file_path: str) -> Tuple[str, str]:
        """
        Parse any supported document type.
        
        Returns:
            Tuple of (text_content, file_type)
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return DocumentParser.parse_pdf(file_path), 'pdf'
        elif file_extension == '.docx':
            return DocumentParser.parse_docx(file_path), 'docx'
        elif file_extension == '.txt':
            return DocumentParser.parse_txt(file_path), 'txt'
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    @staticmethod
    def parse_directory(directory_path: str) -> List[Tuple[str, str, str]]:
        """
        Parse all supported documents in a directory.
        
        Returns:
            List of (file_name, text_content, file_type)
        """
        documents = []
        supported_extensions = {'.pdf', '.docx', '.txt'}
        
        for file_path in Path(directory_path).iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    text, file_type = DocumentParser.parse_document(str(file_path))
                    documents.append((file_path.name, text, file_type))
                    print(f"✓ Parsed: {file_path.name}")
                except Exception as e:
                    print(f"✗ Error parsing {file_path.name}: {str(e)}")
        
        return documents