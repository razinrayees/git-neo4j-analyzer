"""
Utility helper functions for the GitHub Neo4j Analyzer
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any

def clean_string(text: Optional[str]) -> Optional[str]:
    """Clean and sanitize string input"""
    if not text:
        return None
    
    # Remove excessive whitespace and special characters
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned if cleaned else None

def validate_username(username: str) -> bool:
    """Validate GitHub username format"""
    if not username:
        return False
    
    # GitHub username rules: alphanumeric, hyphens, max 39 chars
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, username))

def format_number(num: int) -> str:
    """Format numbers with appropriate suffixes (K, M, B)"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def calculate_language_percentages(languages: Dict[str, int]) -> Dict[str, float]:
    """Calculate percentage distribution of programming languages"""
    if not languages:
        return {}
    
    total_bytes = sum(languages.values())
    if total_bytes == 0:
        return {}
    
    percentages = {}
    for lang, bytes_count in languages.items():
        percentages[lang] = (bytes_count / total_bytes) * 100
    
    return percentages

def sort_repositories(repositories: List[Dict[str, Any]], sort_by: str = 'stars') -> List[Dict[str, Any]]:
    """Sort repositories by specified criteria"""
    valid_sort_fields = ['stars', 'forks', 'updated_at', 'created_at', 'name']
    
    if sort_by not in valid_sort_fields:
        sort_by = 'stars'
    
    reverse_order = sort_by != 'name'  # Name should be alphabetical
    
    try:
        if sort_by in ['updated_at', 'created_at']:
            # Handle datetime sorting
            return sorted(
                repositories,
                key=lambda x: datetime.fromisoformat(x.get(sort_by, '1970-01-01T00:00:00Z').replace('Z', '+00:00')),
                reverse=reverse_order
            )
        else:
            return sorted(
                repositories,
                key=lambda x: x.get(sort_by, 0),
                reverse=reverse_order
            )
    except (ValueError, TypeError):
        # Fallback to stars if sorting fails
        return sorted(repositories, key=lambda x: x.get('stars', 0), reverse=True)

def filter_repositories(repositories: List[Dict[str, Any]], 
                       min_stars: int = 0, 
                       exclude_forks: bool = False,
                       language: Optional[str] = None) -> List[Dict[str, Any]]:
    """Filter repositories based on criteria"""
    filtered = repositories
    
    # Filter by minimum stars
    if min_stars > 0:
        filtered = [repo for repo in filtered if repo.get('stars', 0) >= min_stars]
    
    # Exclude forks
    if exclude_forks:
        filtered = [repo for repo in filtered if not repo.get('is_fork', False)]
    
    # Filter by language
    if language:
        filtered = [repo for repo in filtered if repo.get('language', '').lower() == language.lower()]
    
    return filtered

def get_top_languages(language_stats: Dict[str, Dict], limit: int = 10) -> List[Dict[str, Any]]:
    """Get top programming languages by repository count"""
    if not language_stats:
        return []
    
    languages = []
    for lang_name, stats in language_stats.items():
        languages.append({
            'name': lang_name,
            'repo_count': stats.get('repo_count', 0),
            'total_bytes': stats.get('total_bytes', 0),
            'avg_percentage': stats.get('avg_percentage', 0)
        })
    
    # Sort by repository count
    languages.sort(key=lambda x: x['repo_count'], reverse=True)
    
    return languages[:limit]

def calculate_repository_stats(repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate statistics for repositories"""
    if not repositories:
        return {
            'total_repos': 0,
            'total_stars': 0,
            'total_forks': 0,
            'avg_stars': 0,
            'avg_forks': 0,
            'fork_count': 0,
            'original_count': 0,
            'languages_used': 0
        }
    
    total_stars = sum(repo.get('stars', 0) for repo in repositories)
    total_forks = sum(repo.get('forks', 0) for repo in repositories)
    fork_count = sum(1 for repo in repositories if repo.get('is_fork', False))
    original_count = len(repositories) - fork_count
    
    # Count unique languages
    languages = set()
    for repo in repositories:
        if repo.get('language'):
            languages.add(repo['language'])
    
    return {
        'total_repos': len(repositories),
        'total_stars': total_stars,
        'total_forks': total_forks,
        'avg_stars': total_stars / len(repositories) if repositories else 0,
        'avg_forks': total_forks / len(repositories) if repositories else 0,
        'fork_count': fork_count,
        'original_count': original_count,
        'languages_used': len(languages)
    }

def create_graph_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create graph visualization data structure"""
    if not user_data:
        return {'nodes': [], 'edges': []}
    
    nodes = []
    edges = []
    
    user_stats = user_data.get('user_stats', {})
    repositories = user_stats.get('repositories', [])
    language_stats = user_stats.get('language_stats', {})
    
    # Add user node
    user_node = {
        'id': user_stats.get('username', 'unknown'),
        'label': user_stats.get('username', 'unknown'),
        'type': 'user',
        'size': 30,
        'color': '#3B82F6'
    }
    nodes.append(user_node)
    
    # Add repository nodes and edges
    for repo in repositories[:20]:  # Limit for visualization
        repo_node = {
            'id': repo.get('full_name', repo.get('name', 'unknown')),
            'label': repo.get('name', 'unknown'),
            'type': 'repository',
            'size': min(20, max(8, (repo.get('stars', 0) / 100) + 8)),
            'color': '#14B8A6'
        }
        nodes.append(repo_node)
        
        # Add edge from user to repository
        edges.append({
            'source': user_stats.get('username', 'unknown'),
            'target': repo.get('full_name', repo.get('name', 'unknown')),
            'type': 'owns'
        })
    
    # Add language nodes and edges
    for lang_name in list(language_stats.keys())[:10]:  # Top 10 languages
        lang_node = {
            'id': f"lang_{lang_name}",
            'label': lang_name,
            'type': 'language',
            'size': min(15, max(6, language_stats[lang_name].get('repo_count', 1) * 2)),
            'color': '#F97316'
        }
        nodes.append(lang_node)
        
        # Add edges from repositories to languages
        for repo in repositories:
            if repo.get('language') == lang_name:
                edges.append({
                    'source': repo.get('full_name', repo.get('name', 'unknown')),
                    'target': f"lang_{lang_name}",
                    'type': 'uses_language'
                })
    
    return {
        'nodes': nodes,
        'edges': edges
    }