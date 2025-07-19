import { API_BASE_URL } from '../config/api';

export interface GitHubUser {
  login: string;
  name: string | null;
  bio: string | null;
  location: string | null;
  company: string | null;
  blog: string | null;
  email: string | null;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string;
  updated_at: string;
  avatar_url: string;
}

export interface Repository {
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  stargazers_count: number;
  forks_count: number;
  watchers_count: number;
  size: number;
  fork: boolean;
  private: boolean;
  created_at: string;
  updated_at: string;
  pushed_at: string | null;
  clone_url: string;
  html_url: string;
  topics: string[];
}

export interface LanguageStats {
  [language: string]: number;
}

const GITHUB_API_BASE = 'https://api.github.com';

// Use our backend API instead of direct GitHub API calls
export async function fetchGitHubUserData(username: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze/${username}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.error || 'Analysis failed');
    }
    
    // Transform the API response to match our expected format
    const { user_stats, top_repositories } = result.data;
    
    return {
      user: {
        login: user_stats.username,
        name: user_stats.name,
        bio: null,
        location: null,
        company: null,
        blog: null,
        email: null,
        public_repos: user_stats.total_repos_github,
        followers: 0,
        following: 0,
        created_at: '',
        updated_at: '',
        avatar_url: `https://github.com/${user_stats.username}.png`
      },
      repositories: top_repositories || [],
      languageStats: user_stats.language_stats || {}
    };
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to fetch GitHub data');
  }
}

// Keep the original functions for direct GitHub API access if needed
export async function fetchGitHubUser(username: string): Promise<GitHubUser> {
  const response = await fetch(`${GITHUB_API_BASE}/users/${username}`);
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`User '${username}' not found`);
    }
    throw new Error(`GitHub API error: ${response.status}`);
  }
  
  return response.json();
}

export async function fetchUserRepositories(username: string): Promise<Repository[]> {
  const repositories: Repository[] = [];
  let page = 1;
  const perPage = 100;
  
  while (true) {
    const response = await fetch(
      `${GITHUB_API_BASE}/users/${username}/repos?type=public&sort=updated&per_page=${perPage}&page=${page}`
    );
    
    if (!response.ok) {
      throw new Error(`Failed to fetch repositories: ${response.status}`);
    }
    
    const repos: Repository[] = await response.json();
    
    if (repos.length === 0) {
      break;
    }
    
    repositories.push(...repos);
    
    if (repos.length < perPage) {
      break;
    }
    
    page++;
  }
  
  return repositories;
}

export async function fetchRepositoryLanguages(username: string, repoName: string): Promise<LanguageStats> {
  try {
    const response = await fetch(`${GITHUB_API_BASE}/repos/${username}/${repoName}/languages`);
    
    if (!response.ok) {
      return {};
    }
    
    return response.json();
  } catch {
    return {};
  }
}

export async function fetchGitHubUserDataDirect(username: string) {
  try {
    // Fetch user info
    const user = await fetchGitHubUser(username);
    
    // Fetch repositories
    const repositories = await fetchUserRepositories(username);
    
    // Fetch language data for each repository (limited to avoid rate limits)
    const reposWithLanguages = await Promise.all(
      repositories.slice(0, 20).map(async (repo) => {
        if (!repo.fork) {
          const languages = await fetchRepositoryLanguages(username, repo.name);
          return { ...repo, languages };
        }
        return { ...repo, languages: {} };
      })
    );
    
    // Calculate language statistics
    const languageStats: { [key: string]: { repo_count: number; total_bytes: number } } = {};
    
    reposWithLanguages.forEach(repo => {
      if (repo.languages) {
        Object.entries(repo.languages).forEach(([lang, bytes]) => {
          if (!languageStats[lang]) {
            languageStats[lang] = { repo_count: 0, total_bytes: 0 };
          }
          languageStats[lang].repo_count += 1;
          languageStats[lang].total_bytes += bytes as number;
        });
      }
    });
    
    return {
      user,
      repositories: reposWithLanguages,
      languageStats
    };
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to fetch GitHub data');
  }
}