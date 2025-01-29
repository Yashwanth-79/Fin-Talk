import os
from langchain_groq import ChatGroq
from langchain_community.tools import BraveSearch
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from datetime import datetime
from transformers import pipeline
from typing import List, Dict
import re
from pydantic.v1 import BaseModel

# --------------------------- API KEYS ---------------------------
NEWS_API_KEY = "ca232d0ca1de49f5ba86731e0d6839d4"
FMP_API_KEY = "1PCcILly9sZFq7lSTu9eDNxOxy85Rdl1"
GROQ_API_KEY = "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"
BRAVE_API_KEY = "BSAHkqCaI8WeYS23hfogkBl19fy-tjn"

# --------------------------- FETCH FUNCTIONS ---------------------------
def fetch_news(query, page=1, page_size=30):
    """Fetch news articles using NewsAPI."""
    BASE_URL = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": page_size,
        "page": page
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# --------------------------- CLEANING FUNCTIONS ---------------------------
def clean_news_data(raw_news_data):
    """Clean news data by removing HTML tags and normalizing dates using standard Python."""
    articles = raw_news_data.get("articles", [])
    cleaned_data = []
    for article in articles:
        description = article.get("description", "") or ""
        content = article.get("content", "") or ""
        try:
            cleaned_description = re.sub(r'<[^>]*>', '', description)
            cleaned_content = re.sub(r'<[^>]*>', '', content)
            cleaned_data.append({
                "title": article.get("title", "Untitled"),
                "description": cleaned_description,
                "content": cleaned_content,
                "published_at": datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                if article.get("publishedAt") else "Unknown",
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", "No URL")
            })
        except Exception as e:
            print(f"Error cleaning article: {e}")
    return cleaned_data

# --------------------------- NLP MODELS ---------------------------
ner_pipe = pipeline("token-classification", model="dbmdz/bert-large-cased-finetuned-conll03-english")
sentiment_pipe = pipeline("sentiment-analysis", model="ProsusAI/finbert")
qa_pipe = pipeline("question-answering", model="mrm8488/bert-tiny-finetuned-squadv2")

def extract_entities_hf(text: str) -> str:
    entities = ner_pipe(text)
    return "; ".join([f"{entity['word']} ({entity['entity']})" for entity in entities])

def analyze_sentiment_hf(text: str) -> str:
    result = sentiment_pipe(text)
    return result[0]['label'] if result else "unknown"

def extract_relationships_hf(context: str, question: str) -> str:
    response = qa_pipe(question=question, context=context)
    return response.get('answer', '')

# --------------------------- MAIN FUNCTION ---------------------------
def data_process():
    print("Fetching news articles...")
    raw_news_data = fetch_news(initial_query)
    result_strings = []
    if raw_news_data:
        cleaned_news = clean_news_data(raw_news_data)
        for article in cleaned_news:
            title = article["title"]
            content = article["content"]
            entities = extract_entities_hf(content)
            sentiment = analyze_sentiment_hf(content)
            relationship = extract_relationships_hf(content, "What is the relationship described in this text?")
            result_strings.append({
                "Title": title,
                "Entities": entities,
                "Sentiment": sentiment,
                "Relationship": relationship,
                "Published At": article["published_at"],
                "Source": article["source"],
                "URL": article["url"]
            })
    else:
        print("Failed to fetch news articles.")
    return result_strings

# --------------------------- LLM AND EMBEDDING MODEL ---------------------------
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_tokens=None, max_retries=2, groq_api_key=GROQ_API_KEY)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
tool = BraveSearch.from_api_key(api_key=BRAVE_API_KEY, search_kwargs={"count": 10})
vector_store = None
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def ingest_data_to_faiss(data, embeddings):
    global vector_store
    docs = [f"""
        Title: {item['Title']}
        Entities: {item['Entities']}
        Sentiment: {item['Sentiment']}
        Relationship: {item['Relationship']}
        Source: {item['Source']}
        URL: {item['URL']}
    """ for item in data]
    split_docs = text_splitter.split_text("\n".join(docs))
    vector_store = FAISS.from_texts(split_docs, embeddings)
    print("Data ingested into FAISS.")

# --------------------------- PROMPT TEMPLATE ---------------------------
template = """
You are a financial expert assistant. Answer the user's question politely and formally.
Let the output be well-structured in paragraphs and bullet points.
Answer only finance-related questions.

Chat History:
{chat_history}

Context:
{context}

Question:
{question}
"""
prompt = PromptTemplate(template=template, input_variables=["context", "question", "chat_history"])

def create_rag_chain(llm, vector_store, tool, prompt):
    retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    return ({"context": retriever | (lambda docs: "\n\n".join(doc.page_content for doc in docs)), "question": RunnablePassthrough(), "chat_history": RunnablePassthrough()} | prompt | llm | StrOutputParser())

# --------------------------- MAIN EXECUTION ---------------------------
chat_history = []
initial_query = input("Enter search topic: ")
data = data_process()
if data:
    ingest_data_to_faiss(data, embeddings)
    rag_chain = create_rag_chain(llm, vector_store, tool, prompt)
    while True:
        query = input("Enter your query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        response = rag_chain.invoke(query, chat_history="\n".join(chat_history))
        chat_history.append(f"User: {query}\nAssistant: {response}")
        print(f"Response:\n{response}")
