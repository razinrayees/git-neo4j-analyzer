import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the GitHub Neo4j Analyzer"""
    
    # GitHub API Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_API_BASE_URL = 'https://api.github.com'
    
    # Neo4j Configuration
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Rate Limiting
    GITHUB_REQUESTS_PER_HOUR = 5000 if GITHUB_TOKEN else 60
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        missing_vars = []
        
        if not cls.GITHUB_TOKEN:
            print("Warning: GITHUB_TOKEN not set. API rate limiting will be severe.")
        
        if not cls.NEO4J_URI:
            missing_vars.append('NEO4J_URI')
        
        if not cls.NEO4J_PASSWORD:
            missing_vars.append('NEO4J_PASSWORD')
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True