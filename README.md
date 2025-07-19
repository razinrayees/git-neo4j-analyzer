# GitHub User Network Analyzer

A full-stack application that analyzes GitHub user networks using Python, Neo4j graph database, and a modern web frontend. This tool fetches GitHub user repositories, extracts programming language data, and stores everything in a Neo4j graph database for powerful network analysis.

![GitHub Network Analyzer](static/sample_graph.png)

## 🌟 Features

- **GitHub API Integration**: Fetch user profiles and repository data
- **Neo4j Graph Database**: Store and analyze data in a graph structure
- **Network Analysis**: Discover relationships between users, repositories, and programming languages
- **Modern Web Interface**: Clean, responsive frontend with interactive visualizations
- **RESTful API**: Flask-based backend with comprehensive endpoints
- **Real-time Analysis**: Instant insights into coding patterns and technology stacks

## 🏗️ Architecture

```
(:User {login})-[:OWNS]->(:Repo {name})
(:Repo)-[:USES_LANGUAGE]->(:Language {name})
```

### Graph Schema

- **User Nodes**: GitHub user information (login, name, bio, stats)
- **Repository Nodes**: Repository details (name, description, stars, forks)
- **Language Nodes**: Programming languages used
- **Relationships**: 
  - `OWNS`: User owns repository
  - `USES_LANGUAGE`: Repository uses programming language (with percentage data)

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask, Neo4j Python Driver
- **Database**: Neo4j (Graph Database)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript, Chart.js
- **API**: GitHub REST API v3
- **Deployment**: Gunicorn, Docker-ready

## 📋 Prerequisites

- Python 3.8 or higher
- Neo4j Database (local installation or Neo4j Aura)
- GitHub Personal Access Token (recommended for higher rate limits)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/github-neo4j-analyzer.git
cd github-neo4j-analyzer
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GITHUB_TOKEN=your_github_personal_access_token_here
NEO4J_URI=neo4j+s://your-neo4j-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

### 4. Set Up Neo4j Database

#### Option A: Neo4j Aura (Cloud)
1. Go to [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create a free instance
3. Note your connection details

#### Option B: Local Installation
1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new database
3. Start the database

### 5. Run the Application

```bash
# Start the Flask backend
cd backend
python app.py

# In another terminal, serve the frontend
cd frontend
python -m http.server 8000
```

Visit `http://localhost:8000` to access the application.

## 📖 Usage

### Web Interface

1. **Enter Username**: Type a GitHub username in the search box
2. **Analyze**: Click "Analyze Network" to fetch and process data
3. **Explore Results**: View user statistics, language distribution, and top repositories
4. **Graph Visualization**: See the network structure (placeholder for now)

### API Endpoints

#### Analyze User
```bash
POST /api/analyze/<username>
```

#### Get User Statistics
```bash
GET /api/user/<username>/stats
```

#### Get User Repositories
```bash
GET /api/user/<username>/repositories?limit=10
```

#### Get Network Graph Data
```bash
GET /api/network/graph/<username>
```

### Command Line Usage

```bash
# Fetch GitHub data
python backend/fetch_github.py octocat

# Import to Neo4j
python backend/neo4j_import.py octocat
```

## 🔍 Example Cypher Queries

### Find all repositories for a user
```cypher
MATCH (u:User {login: "octocat"})-[:OWNS]->(r:Repo)
RETURN r.name, r.description, r.stars, r.forks
ORDER BY r.stars DESC
```

### Most popular programming languages
```cypher
MATCH (l:Language)<-[rel:USES_LANGUAGE]-(r:Repo)
WITH l.name as language, count(r) as repo_count
RETURN language, repo_count
ORDER BY repo_count DESC
LIMIT 10
```

### Language diversity analysis
```cypher
MATCH (u:User)-[:OWNS]->(r:Repo)-[:USES_LANGUAGE]->(l:Language)
WITH u, count(DISTINCT l) as language_count
WHERE language_count > 5
RETURN u.login, language_count
ORDER BY language_count DESC
```

See `cypher_queries.txt` for more advanced queries.

## 📁 Project Structure

```
github-neo4j-analyzer/
├── backend/
│   ├── app.py              # Flask application
│   ├── fetch_github.py     # GitHub API client
│   ├── neo4j_import.py     # Neo4j operations
│   ├── config.py           # Configuration management
│   └── utils/              # Utility functions
├── frontend/
│   ├── index.html          # Main webpage
│   ├── app.js             # JavaScript application
│   └── styles.css         # Additional styles
├── static/
│   └── sample_graph.png   # Sample visualization
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── README.md             # This file
└── cypher_queries.txt    # Example Cypher queries
```

## 🔧 Configuration

### GitHub API Rate Limits
- **With Token**: 5,000 requests/hour
- **Without Token**: 60 requests/hour

### Neo4j Configuration
- **Memory**: Recommended 2GB+ for large datasets
- **Indexes**: Automatically created for optimal performance

## 🚢 Deployment

### Using Docker

```bash
# Build the image
docker build -t github-analyzer .

# Run the container
docker run -p 5000:5000 --env-file .env github-analyzer
```

### Using Gunicorn

```bash
cd backend
gunicorn --bind 0.0.0.0:5000 app:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Neo4j** for the powerful graph database
- **GitHub API** for providing comprehensive repository data
- **Chart.js** for beautiful data visualizations
- **Tailwind CSS** for modern styling

## 📞 Support

For questions or support, please open an issue on GitHub or contact [your-email@example.com](mailto:your-email@example.com).

---

**Made with ❤️ using Python, Neo4j, and modern web technologies**