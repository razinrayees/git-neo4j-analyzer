# Complete Setup Guide: GitHub User Network Analyzer with Neo4j Aura

## Step 1: Create Neo4j Aura Account and Database

### 1.1 Sign Up for Neo4j Aura
1. Go to [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/)
2. Click "Start Free" 
3. Create account with email/password or use Google/GitHub login
4. Verify your email address

### 1.2 Create Your First Database
1. After login, click "Create Database"
2. Choose "AuraDB Free" (perfect for this project)
3. Configure your database:
   - **Name**: `github-analyzer` (or any name you prefer)
   - **Region**: Choose closest to your location
   - **Version**: Latest stable version (5.x)
4. Click "Create Database"

### 1.3 Save Your Credentials
**CRITICAL**: Neo4j will show you the credentials ONLY ONCE!

You'll see a screen with:
```
Connection URI: neo4j+s://xxxxxxxx.databases.neo4j.io
Username: neo4j
Password: [generated-password]
```

**IMMEDIATELY SAVE THESE** - you cannot recover the password later!

### 1.4 Download Connection Details
1. Click "Download and Continue"
2. Save the `.txt` file with your credentials
3. Click "Continue" to access your database

## Step 2: Get GitHub Personal Access Token

### 2.1 Create GitHub Token
1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Configure token:
   - **Note**: `GitHub Analyzer Neo4j`
   - **Expiration**: 90 days (or longer)
   - **Scopes**: Select `public_repo` (read access to public repositories)
4. Click "Generate token"
5. **COPY THE TOKEN IMMEDIATELY** - you won't see it again!

## Step 3: Set Up Local Environment

### 3.1 Install Python and Dependencies
```bash
# Check Python version (need 3.8+)
python --version

# Create virtual environment
python -m venv github-analyzer-env

# Activate virtual environment
# On Windows:
github-analyzer-env\Scripts\activate
# On macOS/Linux:
source github-analyzer-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Configure Environment Variables
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your credentials:
```env
# GitHub Configuration
GITHUB_TOKEN=ghp_your_github_token_here

# Neo4j Aura Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

## Step 4: Test Neo4j Connection

### 4.1 Test Database Connection
```bash
cd backend
python -c "
from config import Config
from neo4j_import import Neo4jImporter

try:
    Config.validate_config()
    with Neo4jImporter() as importer:
        print('✅ Neo4j connection successful!')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### 4.2 Test GitHub API
```bash
python -c "
from fetch_github import fetch_user_data

try:
    data = fetch_user_data('octocat')
    print(f'✅ GitHub API working! Found user: {data[\"user\"][\"login\"]}')
except Exception as e:
    print(f'❌ GitHub API failed: {e}')
"
```

## Step 5: Run Your First Analysis

### 5.1 Analyze a GitHub User
```bash
# Test with GitHub's mascot account
python neo4j_import.py octocat
```

You should see output like:
```
Fetching data for user: octocat
Found user: octocat (The Octocat)
Found 8 repositories
Imported user: octocat
Imported repository: octocat/Hello-World
...
Successfully imported data for octocat
```

### 5.2 Verify Data in Neo4j Browser
1. Go to your Neo4j Aura console
2. Click "Open" next to your database
3. This opens Neo4j Browser
4. Run this query to see your data:
```cypher
MATCH (u:User {login: "octocat"})-[:OWNS]->(r:Repo)
RETURN u, r
LIMIT 10
```

## Step 6: Start the Full Application

### 6.1 Start Flask Backend
```bash
cd backend
python app.py
```

You should see:
```
Configuration validated successfully
 * Running on http://0.0.0.0:5000
```

### 6.2 Start Frontend (New Terminal)
```bash
# Open new terminal, navigate to project
cd frontend
python -m http.server 8000
```

### 6.3 Access the Application
1. Open browser to `http://localhost:8000`
2. Enter a GitHub username (try: `octocat`, `torvalds`, `gaearon`)
3. Click "Analyze Network"
4. Watch as it fetches data and stores in Neo4j!

## Step 7: Explore Your Data

### 7.1 Cool Queries to Try in Neo4j Browser

**See all users:**
```cypher
MATCH (u:User) 
RETURN u.login, u.name, u.public_repos
ORDER BY u.public_repos DESC
```

**Most popular languages:**
```cypher
MATCH (l:Language)<-[rel:USES_LANGUAGE]-(r:Repo)
WITH l.name as language, count(r) as repo_count
RETURN language, repo_count
ORDER BY repo_count DESC
LIMIT 10
```

**User's language diversity:**
```cypher
MATCH (u:User {login: "octocat"})-[:OWNS]->(r:Repo)-[:USES_LANGUAGE]->(l:Language)
RETURN l.name, count(r) as repos
ORDER BY repos DESC
```

**Repository network:**
```cypher
MATCH (u:User)-[:OWNS]->(r:Repo)-[:USES_LANGUAGE]->(l:Language)
RETURN u, r, l
LIMIT 50
```

## Step 8: API Endpoints

Your Flask backend provides these endpoints:

```bash
# Analyze new user
curl -X POST http://localhost:5000/api/analyze/username

# Get user stats
curl http://localhost:5000/api/user/username/stats

# Get repositories
curl http://localhost:5000/api/user/username/repositories

# Get network graph data
curl http://localhost:5000/api/network/graph/username
```

## Troubleshooting

### Common Issues:

**1. "Authentication failed" (Neo4j)**
- Double-check your Neo4j URI, username, and password in `.env`
- Ensure your Neo4j instance is running in Aura console

**2. "Rate limit exceeded" (GitHub)**
- Make sure your GitHub token is correctly set in `.env`
- Wait for rate limit to reset (1 hour)

**3. "Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**4. "Connection refused" (Flask)**
- Check if Flask is running on port 5000
- Try `python backend/app.py` from project root

### Getting Help:

**Neo4j Browser Queries:**
- Use the built-in query examples
- Check the "Help" section in Neo4j Browser

**GitHub API Limits:**
- Without token: 60 requests/hour
- With token: 5,000 requests/hour

## Next Steps

1. **Analyze Multiple Users**: Try different GitHub usernames
2. **Explore Relationships**: Use advanced Cypher queries
3. **Visualize Networks**: Export data for visualization tools
4. **Scale Up**: Deploy to cloud with Docker

## Production Deployment

For production deployment:

```bash
# Build Docker image
docker build -t github-analyzer .

# Run with Docker Compose (includes Neo4j)
docker-compose up -d
```

**Congratulations!** 🎉 You now have a fully functional GitHub User Network Analyzer with Neo4j Aura integration!