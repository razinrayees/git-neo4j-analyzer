from neo4j import GraphDatabase
from typing import Dict, List
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jImporter:
    """Neo4j database importer for GitHub user and repository data"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD)
        )
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def clear_database(self):
        """Clear all nodes and relationships in the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")
    
    def create_constraints(self):
        """Create unique constraints for better performance and data integrity"""
        constraints = [
            "CREATE CONSTRAINT user_login IF NOT EXISTS FOR (u:User) REQUIRE u.login IS UNIQUE",
            "CREATE CONSTRAINT repo_full_name IF NOT EXISTS FOR (r:Repo) REQUIRE r.full_name IS UNIQUE",
            "CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Failed to create constraint: {e}")
    
    def import_user(self, user_data: Dict) -> None:
        """Import user data into Neo4j"""
        query = """
        MERGE (u:User {login: $login})
        SET u.name = $name,
            u.bio = $bio,
            u.location = $location,
            u.company = $company,
            u.blog = $blog,
            u.email = $email,
            u.public_repos = $public_repos,
            u.followers = $followers,
            u.following = $following,
            u.created_at = $created_at,
            u.updated_at = $updated_at,
            u.avatar_url = $avatar_url,
            u.last_analyzed = datetime()
        RETURN u
        """
        
        with self.driver.session() as session:
            result = session.run(query, **user_data)
            logger.info(f"Imported user: {user_data['login']}")
            return result.single()
    
    def import_repository(self, repo_data: Dict, username: str) -> None:
        """Import repository data and create relationship with user"""
        query = """
        MATCH (u:User {login: $username})
        MERGE (r:Repo {full_name: $full_name})
        SET r.name = $name,
            r.description = $description,
            r.language = $language,
            r.stars = $stars,
            r.forks = $forks,
            r.watchers = $watchers,
            r.size = $size,
            r.is_fork = $is_fork,
            r.is_private = $is_private,
            r.created_at = $created_at,
            r.updated_at = $updated_at,
            r.pushed_at = $pushed_at,
            r.clone_url = $clone_url,
            r.html_url = $html_url,
            r.topics = $topics
        MERGE (u)-[:OWNS]->(r)
        RETURN r
        """
        
        with self.driver.session() as session:
            repo_params = {**repo_data, 'username': username}
            result = session.run(query, **repo_params)
            logger.info(f"Imported repository: {repo_data['full_name']}")
            return result.single()
    
    def import_languages(self, repo_full_name: str, languages: Dict[str, int]) -> None:
        """Import programming languages and create relationships with repository"""
        if not languages:
            return
        
        # Calculate total bytes for percentage calculation
        total_bytes = sum(languages.values())
        
        for language, bytes_count in languages.items():
            percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
            
            query = """
            MATCH (r:Repo {full_name: $repo_full_name})
            MERGE (l:Language {name: $language})
            MERGE (r)-[rel:USES_LANGUAGE]->(l)
            SET rel.bytes = $bytes_count,
                rel.percentage = $percentage
            RETURN l, rel
            """
            
            with self.driver.session() as session:
                session.run(query, {
                    'repo_full_name': repo_full_name,
                    'language': language,
                    'bytes_count': bytes_count,
                    'percentage': percentage
                })
        
        logger.info(f"Imported {len(languages)} languages for {repo_full_name}")
    
    def import_complete_user_data(self, data: Dict) -> None:
        """Import complete user data including repositories and languages"""
        user_data = data['user']
        repositories = data['repositories']
        
        logger.info(f"Starting import for user: {user_data['login']}")
        
        # Import user
        self.import_user(user_data)
        
        # Import repositories
        for repo in repositories:
            self.import_repository(repo, user_data['login'])
            
            # Import languages for this repository
            if 'languages' in repo and repo['languages']:
                self.import_languages(repo['full_name'], repo['languages'])
        
        logger.info(f"Completed import for user: {user_data['login']}")
    
    def get_user_stats(self, username: str) -> Dict:
        """Get comprehensive stats for a user from Neo4j"""
        query = """
        MATCH (u:User {login: $username})
        OPTIONAL MATCH (u)-[:OWNS]->(r:Repo)
        OPTIONAL MATCH (r)-[rel:USES_LANGUAGE]->(l:Language)
        
        WITH u, r, l, rel
        
        RETURN u.login as username,
               u.name as name,
               u.public_repos as total_repos_github,
               count(DISTINCT r) as repos_analyzed,
               collect(DISTINCT {
                   name: r.name,
                   full_name: r.full_name,
                   description: r.description,
                   stars: r.stars,
                   forks: r.forks,
                   language: r.language,
                   is_fork: r.is_fork,
                   topics: r.topics
               }) as repositories,
               collect(DISTINCT {
                   language: l.name,
                   percentage: rel.percentage,
                   bytes: rel.bytes
               }) as languages
        """
        
        with self.driver.session() as session:
            result = session.run(query, username=username)
            record = result.single()
            
            if not record:
                return None
            
            # Process language statistics
            languages = [lang for lang in record['languages'] if lang['language']]
            language_stats = {}
            
            for lang in languages:
                lang_name = lang['language']
                if lang_name not in language_stats:
                    language_stats[lang_name] = {
                        'total_bytes': 0,
                        'repo_count': 0,
                        'avg_percentage': 0
                    }
                
                language_stats[lang_name]['total_bytes'] += lang.get('bytes', 0)
                language_stats[lang_name]['repo_count'] += 1
            
            # Calculate average percentages
            for lang_name, stats in language_stats.items():
                if stats['repo_count'] > 0:
                    lang_percentages = [
                        lang['percentage'] for lang in languages 
                        if lang['language'] == lang_name and lang.get('percentage')
                    ]
                    if lang_percentages:
                        stats['avg_percentage'] = sum(lang_percentages) / len(lang_percentages)
            
            return {
                'username': record['username'],
                'name': record['name'],
                'total_repos_github': record['total_repos_github'],
                'repos_analyzed': record['repos_analyzed'],
                'repositories': [repo for repo in record['repositories'] if repo['name']],
                'language_stats': language_stats
            }
    
    def get_top_repositories(self, username: str, limit: int = 10) -> List[Dict]:
        """Get top repositories by stars for a user"""
        query = """
        MATCH (u:User {login: $username})-[:OWNS]->(r:Repo)
        WHERE NOT r.is_fork
        RETURN r.name as name,
               r.full_name as full_name,
               r.description as description,
               r.stars as stars,
               r.forks as forks,
               r.language as language,
               r.html_url as url
        ORDER BY r.stars DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, username=username, limit=limit)
            return [record.data() for record in result]

def import_github_user(username: str, github_data: Dict = None) -> None:
    """Main function to import GitHub user data into Neo4j"""
    try:
        Config.validate_config()
        
        with Neo4jImporter() as importer:
            # Create constraints for better performance
            importer.create_constraints()
            
            # If no data provided, fetch it
            if not github_data:
                from fetch_github import fetch_user_data
                github_data = fetch_user_data(username)
            
            # Import the data
            importer.import_complete_user_data(github_data)
            
            logger.info(f"Successfully imported data for {username}")
            
    except Exception as e:
        logger.error(f"Failed to import data for {username}: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python neo4j_import.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    
    try:
        import_github_user(username)
        print(f"Successfully imported data for {username}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)