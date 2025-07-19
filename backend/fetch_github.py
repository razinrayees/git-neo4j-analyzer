import requests
import time
from typing import Dict, List, Optional
from config import Config

class GitHubAPIClient:
    """GitHub API client for fetching user and repository data"""
    
    def __init__(self):
        self.base_url = Config.GITHUB_API_BASE_URL
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Neo4j-Analyzer/1.0'
        }
        
        if Config.GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {Config.GITHUB_TOKEN}'
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the GitHub API with error handling and rate limiting"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                current_time = int(time.time())
                sleep_time = max(0, reset_time - current_time + 1)
                
                print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
                return self._make_request(url, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"GitHub API request failed: {str(e)}")
    
    def get_user_info(self, username: str) -> Dict:
        """Fetch user information from GitHub API"""
        url = f"{self.base_url}/users/{username}"
        
        try:
            user_data = self._make_request(url)
            return {
                'login': user_data['login'],
                'name': user_data.get('name'),
                'bio': user_data.get('bio'),
                'location': user_data.get('location'),
                'company': user_data.get('company'),
                'blog': user_data.get('blog'),
                'email': user_data.get('email'),
                'public_repos': user_data['public_repos'],
                'followers': user_data['followers'],
                'following': user_data['following'],
                'created_at': user_data['created_at'],
                'updated_at': user_data['updated_at'],
                'avatar_url': user_data['avatar_url']
            }
        except Exception as e:
            if "404" in str(e):
                raise Exception(f"User '{username}' not found")
            raise e
    
    def get_user_repositories(self, username: str, per_page: int = 100) -> List[Dict]:
        """Fetch all public repositories for a user"""
        repositories = []
        page = 1
        
        while True:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                'type': 'public',
                'sort': 'updated',
                'per_page': per_page,
                'page': page
            }
            
            repos_data = self._make_request(url, params)
            
            if not repos_data:
                break
            
            for repo in repos_data:
                repositories.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description'),
                    'language': repo.get('language'),
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'watchers': repo['watchers_count'],
                    'size': repo['size'],
                    'is_fork': repo['fork'],
                    'is_private': repo['private'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'pushed_at': repo.get('pushed_at'),
                    'clone_url': repo['clone_url'],
                    'html_url': repo['html_url'],
                    'topics': repo.get('topics', [])
                })
            
            page += 1
            
            # Break if we got less than requested (last page)
            if len(repos_data) < per_page:
                break
        
        return repositories
    
    def get_repository_languages(self, username: str, repo_name: str) -> Dict[str, int]:
        """Fetch language statistics for a specific repository"""
        url = f"{self.base_url}/repos/{username}/{repo_name}/languages"
        
        try:
            return self._make_request(url)
        except Exception:
            # If languages endpoint fails, return empty dict
            return {}

def fetch_user_data(username: str) -> Dict:
    """Main function to fetch complete user data including repositories and languages"""
    client = GitHubAPIClient()
    
    print(f"Fetching data for user: {username}")
    
    # Get user information
    user_info = client.get_user_info(username)
    print(f"Found user: {user_info['login']} ({user_info.get('name', 'No name')})")
    
    # Get repositories
    repositories = client.get_user_repositories(username)
    print(f"Found {len(repositories)} repositories")
    
    # Get language data for each repository
    for repo in repositories:
        if not repo['is_fork']:  # Only get languages for original repos
            try:
                languages = client.get_repository_languages(username, repo['name'])
                repo['languages'] = languages
            except Exception as e:
                print(f"Warning: Could not fetch languages for {repo['name']}: {e}")
                repo['languages'] = {}
        else:
            repo['languages'] = {}
    
    return {
        'user': user_info,
        'repositories': repositories
    }

if __name__ == "__main__":
    # Test the GitHub API client
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python fetch_github.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    
    try:
        Config.validate_config()
        data = fetch_user_data(username)
        print(f"\nSuccessfully fetched data for {data['user']['login']}")
        print(f"Repositories: {len(data['repositories'])}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)