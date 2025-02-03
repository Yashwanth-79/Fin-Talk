# Fin-Talk: AI-Powered Financial Assistant

Live : https://fintalk-client-oqfcyuzu4-yashwanth-79s-projects.vercel.app/
Demo : https://youtu.be/LkhYakvjRBQ?feature=shared

## 📌 Project Overview
**Fin-Talk** is an AI-powered financial assistant that provides financial insights, real-time news analysis, and conversational AI capabilities. It integrates **LangChain, FAISS, Neo4j, and Groq** to process, retrieve, and analyze financial data while allowing interactive queries.

## 🚀 Features
- 🔍 **News Aggregation & Analysis**: Fetch and clean financial news articles.
- 🧠 **Natural Language Processing (NLP)**: Named Entity Recognition (NER), Sentiment Analysis, and Relationship Extraction using Hugging Face models.
- 📊 **Vector Database (FAISS)**: Stores and retrieves relevant documents efficiently.
- 🏦 **Graph Database (Neo4j)**: Creates and visualizes relationships between financial entities, sentiments, and articles.
- 🤖 **Conversational AI**: Provides intelligent responses using **LangChain RAG** with Groq-powered LLMs.
- 🌐 **Web API with Flask**: RESTful API to interact with the system.
- 🎨 **Graph Visualization**: Generates interactive HTML visualizations of financial entities and relationships.

## 🏗️ Tech Stack
| Technology | Description |
|------------|-------------|
| **Flask** | Web framework for building APIs |
| **LangChain** | Framework for LLM-powered applications |
| **Groq LLM** | Powerful AI model for financial queries |
| **FAISS** | Vector database for efficient retrieval |
| **Neo4j** | Graph database for relationship mapping |
| **Hugging Face Transformers** | NLP models for entity recognition & sentiment analysis |
| **Brave Search API** | Fetches real-time financial news |
| **NewsAPI** | Aggregates financial news from various sources |

## 📂 Project Structure
```plaintext
📁 Fin-Talk
│-- 📁 client                # Frontend (HTML, CSS, JS)
│-- 📁 static                # Static files
│-- 📁 templates             # Flask templates
│-- 📄 app.py                # Main Flask application
│-- 📄 requirements.txt      # Dependencies
│-- 📄 README.md             # Project documentation
```

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/fin-talk.git
cd fin-talk
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up API Keys (Rename `.env.example` to `.env` & add keys)
```plaintext
NEWS_API_KEY=your_news_api_key
FMP_API_KEY=your_fmp_api_key
GROQ_API_KEY=your_groq_api_key
BRAVE_API_KEY=your_brave_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

### 5️⃣ Run the Application
```bash
python app.py
```
Server will start at `http://127.0.0.1:5000`

## 📡 API Endpoints

### 🔹 `POST /initial_query`
> **Description:** Fetches and processes financial news, then ingests data into FAISS & Neo4j.
```json
{
  "query": "latest financial trends"
}
```

### 🔹 `POST /conversational_query`
> **Description:** Converses with the AI assistant based on financial news and stored data.
```json
{
  "query": "What is the sentiment of Tesla's latest news?"
}
```

### 🔹 `GET /chat_history`
> **Description:** Fetches the chat history.

### 🔹 `GET /show_graph`
> **Description:** Generates and returns HTML graph visualizations.

## 📈 Graph Visualization
Fin-Talk automatically generates **interactive financial relationship graphs**. Example graphs include:
- **Sentiment Analysis Graph**
- **Entity Relationship Graph**

Open `sentiment_graph.html` and `relationship_graph.html` in your browser to explore!

## 🛠️ Future Enhancements
- ✅ Expand financial data sources
- ✅ Improve entity linking for better knowledge graphs
- ✅ Deploy as a cloud-hosted API
- ✅ Develop a frontend dashboard for better insights

## 🎯 Contributing
Pull requests are welcome! If you'd like to contribute:
1. Fork the repo
2. Create a feature branch (`feature-new`)
3. Commit your changes
4. Open a PR 🚀

## 📝 License
This project is licensed under the **MIT License**.

## 📞 Contact
For queries or collaboration, reach out to **your.email@example.com**

---

_💡 "Empowering financial insights with AI-driven intelligence!"_ 🚀
