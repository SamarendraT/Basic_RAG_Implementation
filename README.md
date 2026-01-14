# Basic RAG Implementation

A **Retrieval-Augmented Generation (RAG)** application that combines vector embeddings with a large language model to answer questions based on stored documents.

## 🎯 Overview

This project implements a RAG system using:
- **Chroma** - Vector database for storing and retrieving document embeddings
- **Ollama** - Local LLM inference engine (using TinyLLaMA)
- **FastAPI** - REST API for querying and adding documents

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher
- pip (Python package manager)
- [Ollama](https://ollama.ai/) installed and running locally
- TinyLLaMA model pulled in Ollama

## 🚀 Step-by-Step Setup & Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/SamarendraT/Basic_RAG_Implementation.git
cd Basic_RAG_Implementation
