import os
from pathlib import Path
from typing import List, Tuple
import PyPDF2
from docx import Document as DocxDocument
import re


class TextChunker:
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        if not text or len(text) <= chunk_size:
            return [text] if text else []

        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks


class DocumentParser:
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
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
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")
    
    @staticmethod
    def parse_document(file_path: str) -> Tuple[str, str]:

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
