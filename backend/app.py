from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from typing import Dict, List

from config import Config
from fetch_github import fetch_user_data
from neo4j_import import Neo4jImporter, import_github_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for production
if Config.FLASK_ENV == 'production':
    # In production, allow requests from the Render frontend domain
    CORS(app, origins=[
        "https://*.onrender.com",
        "https://github-analyzer-frontend.onrender.com"
    ])
else:
    # In development, allow all origins
    CORS(app)

# Validate configuration on startup
try:
    Config.validate_config()
    logger.info("Configuration validated successfully")
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'GitHub Neo4j Analyzer API',
        'version': '1.0.0'
    })

@app.route('/api/analyze/<username>', methods=['POST'])
def analyze_user(username: str):
    """Analyze a GitHub user and store data in Neo4j"""
    try:
        logger.info(f"Starting analysis for user: {username}")
        
        # Fetch GitHub data
        github_data = fetch_user_data(username)
        
        # Import to Neo4j
        import_github_user(username, github_data)
        
        # Get processed stats from Neo4j
        with Neo4jImporter() as importer:
            stats = importer.get_user_stats(username)
            top_repos = importer.get_top_repositories(username, limit=10)
        
        response = {
            'success': True,
            'message': f'Successfully analyzed user: {username}',
            'data': {
                'user_stats': stats,
                'top_repositories': top_repos
            }
        }
        
        logger.info(f"Analysis completed for user: {username}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis failed for user {username}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/user/<username>/stats', methods=['GET'])
def get_user_stats(username: str):
    """Get user statistics from Neo4j"""
    try:
        with Neo4jImporter() as importer:
            stats = importer.get_user_stats(username)
            
            if not stats:
                return jsonify({
                    'success': False,
                    'error': f'No data found for user: {username}'
                }), 404
            
            return jsonify({
                'success': True,
                'data': stats
            })
            
    except Exception as e:
        logger.error(f"Failed to get stats for user {username}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/<username>/repositories', methods=['GET'])
def get_user_repositories(username: str):
    """Get user repositories from Neo4j"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        with Neo4jImporter() as importer:
            repos = importer.get_top_repositories(username, limit)
            
            return jsonify({
                'success': True,
                'data': {
                    'repositories': repos,
                    'count': len(repos)
                }
            })
            
    except Exception as e:
        logger.error(f"Failed to get repositories for user {username}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/languages/popular', methods=['GET'])
def get_popular_languages():
    """Get most popular programming languages across all users"""
    try:
        query = """
        MATCH (l:Language)<-[rel:USES_LANGUAGE]-(r:Repo)
        WITH l.name as language, 
             count(r) as repo_count,
             sum(rel.bytes) as total_bytes,
             avg(rel.percentage) as avg_percentage
        ORDER BY repo_count DESC
        LIMIT 20
        RETURN language, repo_count, total_bytes, avg_percentage
        """
        
        with Neo4jImporter() as importer:
            with importer.driver.session() as session:
                result = session.run(query)
                languages = [record.data() for record in result]
        
        return jsonify({
            'success': True,
            'data': {
                'popular_languages': languages
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get popular languages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/network/graph/<username>', methods=['GET'])
def get_user_network_graph(username: str):
    """Get graph data for visualization"""
    try:
        query = """
        MATCH (u:User {login: $username})-[:OWNS]->(r:Repo)-[rel:USES_LANGUAGE]->(l:Language)
        
        WITH u, r, l, rel
        
        RETURN {
            nodes: collect(DISTINCT {id: u.login, label: u.login, type: 'user'}) +
                   collect(DISTINCT {id: r.full_name, label: r.name, type: 'repo', stars: r.stars}) +
                   collect(DISTINCT {id: l.name, label: l.name, type: 'language'}),
            
            edges: collect(DISTINCT {source: u.login, target: r.full_name, type: 'owns'}) +
                   collect(DISTINCT {source: r.full_name, target: l.name, type: 'uses', weight: rel.percentage})
        } AS graph
        """
        
        with Neo4jImporter() as importer:
            with importer.driver.session() as session:
                result = session.run(query, username=username)
                record = result.single()
                
                if not record:
                    return jsonify({
                        'success': False,
                        'error': f'No graph data found for user: {username}'
                    }), 404
                
                return jsonify({
                    'success': True,
                    'data': record['graph']
                })
        
    except Exception as e:
        logger.error(f"Failed to get graph data for user {username}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        debug=Config.FLASK_DEBUG,
        host='0.0.0.0',
        port=port
    )