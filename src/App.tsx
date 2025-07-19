import React, { useState } from 'react';
import { Search, Github, Star, GitFork, Database, User, ExternalLink, Loader2 } from 'lucide-react';
import { fetchGitHubUserData } from './services/github';
import type { GitHubUser, Repository } from './services/github';

function App() {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [userData, setUserData] = useState<GitHubUser | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [languageStats, setLanguageStats] = useState<{ [key: string]: { repo_count: number; total_bytes: number } }>({});
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!username.trim()) {
      setError('Please enter a GitHub username');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const data = await fetchGitHubUserData(username.trim());
      setUserData(data.user);
      setRepositories(data.repositories);
      setLanguageStats(data.languageStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setUserData(null);
      setRepositories([]);
      setLanguageStats({});
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  const totalStars = repositories.reduce((sum, repo) => sum + repo.stargazers_count, 0);
  const totalForks = repositories.reduce((sum, repo) => sum + repo.forks_count, 0);
  const topLanguage = Object.keys(languageStats).reduce((a, b) => 
    languageStats[a]?.repo_count > languageStats[b]?.repo_count ? a : b, 
    Object.keys(languageStats)[0] || 'N/A'
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Github className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-slate-900">GitHub Network Analyzer</h1>
            </div>
            <div className="flex items-center space-x-2 text-sm text-slate-600">
              <Database className="w-4 h-4" />
              <span>Powered by Neo4j</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-slate-900 mb-4">
            Analyze GitHub User Networks
          </h2>
          <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
            Enter a GitHub username to explore their repositories, programming languages, and project statistics stored in a Neo4j graph database
          </p>
          
          <div className="max-w-md mx-auto">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter GitHub username..."
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-lg"
                disabled={loading}
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 text-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Network'
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-300 text-red-700 rounded-lg max-w-md mx-auto">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {userData && (
          <div className="fade-in">
            {/* User Profile Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
              <div className="flex items-center space-x-6">
                <div className="flex-shrink-0">
                  <img 
                    src={userData.avatar_url} 
                    alt={userData.login}
                    className="w-20 h-20 rounded-full"
                  />
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-slate-900">{userData.login}</h2>
                  {userData.name && <p className="text-lg text-slate-600">{userData.name}</p>}
                  {userData.bio && <p className="text-slate-600 mt-1">{userData.bio}</p>}
                  <div className="flex items-center space-x-4 mt-2 text-sm text-slate-500">
                    <span><Database className="w-4 h-4 inline mr-1" />{repositories.length} repos analyzed</span>
                    <span>{userData.followers} followers</span>
                    <span>{userData.following} following</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <div className="text-3xl font-bold text-blue-600">{repositories.length}</div>
                <div className="text-slate-600">Total Repositories</div>
              </div>
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <div className="text-3xl font-bold text-teal-600">{topLanguage}</div>
                <div className="text-slate-600">Top Language</div>
              </div>
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <div className="text-3xl font-bold text-orange-600">{totalStars.toLocaleString()}</div>
                <div className="text-slate-600">Total Stars</div>
              </div>
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <div className="text-3xl font-bold text-purple-600">{totalForks.toLocaleString()}</div>
                <div className="text-slate-600">Total Forks</div>
              </div>
            </div>

            {/* Charts and Repository List */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Language Chart */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-slate-900 mb-4">Programming Languages</h3>
                <div className="space-y-3">
                  {Object.entries(languageStats)
                    .sort(([,a], [,b]) => b.repo_count - a.repo_count)
                    .slice(0, 8)
                    .map(([lang, stats], index) => (
                    <div key={lang} className="flex items-center justify-between">
                      <span className="font-medium">{lang}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${Math.min(100, (stats.repo_count / Math.max(...Object.values(languageStats).map(s => s.repo_count))) * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-500">{stats.repo_count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Repositories */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-slate-900 mb-4">Top Repositories</h3>
                <div className="space-y-4">
                  {repositories
                    .sort((a, b) => b.stargazers_count - a.stargazers_count)
                    .slice(0, 10)
                    .map((repo) => (
                    <div key={repo.name} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-slate-900">{repo.name}</h4>
                        <div className="flex items-center space-x-3 text-sm text-slate-500">
                          <span className="flex items-center">
                            <Star className="w-4 h-4 mr-1" />
                            {repo.stargazers_count}
                          </span>
                          <span className="flex items-center">
                            <GitFork className="w-4 h-4 mr-1" />
                            {repo.forks_count}
                          </span>
                        </div>
                      </div>
                      {repo.description && <p className="text-sm text-slate-600 mb-2">{repo.description}</p>}
                      <div className="flex items-center justify-between">
                        {repo.language ? (
                          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                            {repo.language}
                          </span>
                        ) : <span></span>}
                        <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 text-sm">
                          <ExternalLink className="w-4 h-4 inline" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Graph Visualization Placeholder */}
            <div className="mt-8 bg-white rounded-xl shadow-lg p-6 max-h-96">
              <h3 className="text-xl font-bold text-slate-900 mb-4">Neo4j Network Graph</h3>
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-8 text-center h-64 flex flex-col justify-center">
                <Database className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                <p className="text-slate-600">Graph visualization would appear here</p>
                <p className="text-sm text-slate-500 mt-2">Connected to Neo4j database for network analysis</p>
                <div className="mt-2 text-xs text-slate-400">
                  <p>Graph Schema: (:User)-[:OWNS]→(:Repo)-[:USES_LANGUAGE]→(:Language)</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;