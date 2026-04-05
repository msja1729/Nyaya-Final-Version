
# Nyaya Sahayak (न्याय सहायक): AI-Powered Legal Assistant for Indian Law

## Project Overview

Nyaya Sahayak is a comprehensive multilingual AI-powered legal information system designed to democratize access to Indian legal knowledge. Built on Databricks with cutting-edge AI technologies, it bridges the gap between complex legal documentation and citizens who need accessible legal guidance in their native language.

## Problem Statement

India's legal system, while robust, remains largely inaccessible to the average citizen due to three critical barriers: (1) legal documents written in complex English terminology, (2) lack of multilingual support for India's linguistically diverse population, and (3) the high cost of legal consultation for basic queries. With over 22 scheduled languages and 70% of the population not fluent in English, millions struggle to understand their fundamental legal rights.

## Solution Architecture

Nyaya Sahayak employs a sophisticated Retrieval-Augmented Generation (RAG) architecture that combines vector search with large language models. The system ingests legal documents (Bharatiya Nyaya Sanhita, Indian Penal Code, Indian Evidence Act) and converts them into 384-dimensional embeddings using sentence-transformers. These embeddings are indexed using FAISS (Facebook AI Similarity Search) for efficient retrieval.

When a user asks a question, the system: (1) translates the query to English using Sarvam Mayura's neural machine translation, (2) retrieves the top-5 most relevant legal passages via cosine similarity search, (3) augments the context and sends it to Databricks' Llama 4 Maverick LLM, and (4) translates the response back to the user's language. This entire pipeline operates on Databricks infrastructure, leveraging Unity Catalog for data governance, AI Gateway for LLM access, and Databricks Apps for deployment.

## Key Features

**Trial of Justice Mode** presents legal questions through adversarial analysis—simulating prosecution and defense arguments followed by a judicial summary. This helps users understand multiple perspectives on complex legal issues.

**Multilingual Support** spans 13 Indian languages (Hindi, Tamil, Bengali, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Urdu, Assamese, and English) using Sarvam AI's state-of-the-art translation APIs.

**Voice Interaction** enables hands-free operation through Sarvam Saaras (speech-to-text) and Bulbul (text-to-speech), automatically transcribing questions, translating them, and speaking answers aloud—critical for users with limited literacy.

**Chitragupta**, named after the Hindu deity of records, provides encrypted chat export/import using AES-256 encryption hidden in PNG images via LSB steganography. This ensures data portability and privacy compliance with India's Digital Personal Data Protection Act 2023.

**Pralaya** (cosmic dissolution) implements the "right to erasure" under DPDP Act 2023, allowing users to permanently delete their conversation history.

## Impact and Use Cases

Nyaya Sahayak serves multiple user segments: citizens seeking quick legal clarifications, students researching Indian law, journalists fact-checking legal claims, and lawyers conducting preliminary research. By reducing the friction in accessing legal information, it empowers individuals to make informed decisions about their rights and obligations.

## Technical Innovation

The project showcases production-grade AI engineering: FAISS for exact similarity search (optimal for ~900 document corpus), zero-shot prompting for adversarial dialogue generation, seq2seq models for multilingual NLP, and end-to-end encryption for privacy-first data handling. The entire system runs serverless on Databricks, demonstrating cloud-native scalability.

## Future Roadmap

Planned enhancements include integration with live court judgment databases, regional legal variations for state-specific laws, WhatsApp bot deployment for feature phone users, and expansion to all 22 scheduled Indian languages.

**Word Count: 500 words**
