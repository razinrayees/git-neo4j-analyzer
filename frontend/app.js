// GitHub Neo4j Analyzer Frontend Application
class GitHubAnalyzer {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.currentUser = null;
        this.languageChart = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        const usernameInput = document.getElementById('usernameInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        // Handle Enter key in input
        usernameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeUser();
            }
        });
        
        // Handle analyze button click
        analyzeBtn.addEventListener('click', () => {
            this.analyzeUser();
        });
    }
    
    async analyzeUser() {
        const username = document.getElementById('usernameInput').value.trim();
        
        if (!username) {
            this.showError('Please enter a GitHub username');
            return;
        }
        
        this.setLoading(true);
        this.hideError();
        this.hideResults();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze/${username}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            this.currentUser = data.data;
            this.displayResults();
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(error.message || 'Failed to analyze user. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    setLoading(loading) {
        const btn = document.getElementById('analyzeBtn');
        const btnText = document.getElementById('btnText');
        const btnLoader = document.getElementById('btnLoader');
        const input = document.getElementById('usernameInput');
        
        if (loading) {
            btn.disabled = true;
            btnText.textContent = 'Analyzing...';
            btnLoader.classList.remove('hidden');
            input.disabled = true;
        } else {
            btn.disabled = false;
            btnText.textContent = 'Analyze Network';
            btnLoader.classList.add('hidden');
            input.disabled = false;
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    hideError() {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.classList.add('hidden');
    }
    
    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.classList.add('hidden');
    }
    
    displayResults() {
        if (!this.currentUser) return;
        
        const { user_stats, top_repositories } = this.currentUser;
        
        // Display user profile
        this.displayUserProfile(user_stats);
        
        // Display stats overview
        this.displayStatsOverview(user_stats, top_repositories);
        
        // Display language chart
        this.displayLanguageChart(user_stats.language_stats);
        
        // Display repository list
        this.displayRepositoryList(top_repositories);
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.classList.remove('hidden');
    }
    
    displayUserProfile(userStats) {
        const profileDiv = document.getElementById('userProfile');
        
        const profileHTML = `
            <div class="flex items-center space-x-6">
                <div class="flex-shrink-0">
                    <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                        <i data-lucide="user" class="w-10 h-10 text-blue-600"></i>
                    </div>
                </div>
                <div class="flex-1">
                    <h2 class="text-2xl font-bold text-slate-900">${userStats.username}</h2>
                    ${userStats.name ? `<p class="text-lg text-slate-600">${userStats.name}</p>` : ''}
                    <div class="flex items-center space-x-4 mt-2 text-sm text-slate-500">
                        <span><i data-lucide="git-branch" class="w-4 h-4 inline mr-1"></i>${userStats.repos_analyzed} repos analyzed</span>
                        <span><i data-lucide="database" class="w-4 h-4 inline mr-1"></i>Stored in Neo4j</span>
                    </div>
                </div>
            </div>
        `;
        
        profileDiv.innerHTML = profileHTML;
        lucide.createIcons();
    }
    
    displayStatsOverview(userStats, topRepos) {
        // Calculate totals
        const totalStars = userStats.repositories.reduce((sum, repo) => sum + (repo.stars || 0), 0);
        const totalForks = userStats.repositories.reduce((sum, repo) => sum + (repo.forks || 0), 0);
        
        // Find top language by repo count
        const topLanguage = Object.keys(userStats.language_stats).reduce((a, b) => 
            userStats.language_stats[a].repo_count > userStats.language_stats[b].repo_count ? a : b, 
            Object.keys(userStats.language_stats)[0] || 'N/A'
        );
        
        document.getElementById('totalRepos').textContent = userStats.repos_analyzed;
        document.getElementById('topLanguage').textContent = topLanguage;
        document.getElementById('totalStars').textContent = totalStars.toLocaleString();
        document.getElementById('totalForks').textContent = totalForks.toLocaleString();
    }
    
    displayLanguageChart(languageStats) {
        const ctx = document.getElementById('languageChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.languageChart) {
            this.languageChart.destroy();
        }
        
        // Prepare data for chart
        const languages = Object.keys(languageStats).slice(0, 8); // Top 8 languages
        const repoCounts = languages.map(lang => languageStats[lang].repo_count);
        
        const colors = [
            '#3B82F6', '#14B8A6', '#F97316', '#8B5CF6',
            '#EF4444', '#10B981', '#F59E0B', '#6366F1'
        ];
        
        this.languageChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: languages,
                datasets: [{
                    data: repoCounts,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    displayRepositoryList(repositories) {
        const listDiv = document.getElementById('repositoryList');
        
        if (!repositories || repositories.length === 0) {
            listDiv.innerHTML = '<p class="text-slate-500">No repositories found</p>';
            return;
        }
        
        const repoHTML = repositories.slice(0, 10).map(repo => `
            <div class="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="font-semibold text-slate-900">${repo.name}</h4>
                    <div class="flex items-center space-x-3 text-sm text-slate-500">
                        <span class="flex items-center">
                            <i data-lucide="star" class="w-4 h-4 mr-1"></i>
                            ${repo.stars}
                        </span>
                        <span class="flex items-center">
                            <i data-lucide="git-fork" class="w-4 h-4 mr-1"></i>
                            ${repo.forks}
                        </span>
                    </div>
                </div>
                ${repo.description ? `<p class="text-sm text-slate-600 mb-2">${repo.description}</p>` : ''}
                <div class="flex items-center justify-between">
                    ${repo.language ? `<span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">${repo.language}</span>` : '<span></span>'}
                    <a href="${repo.url}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i data-lucide="external-link" class="w-4 h-4 inline"></i>
                    </a>
                </div>
            </div>
        `).join('');
        
        listDiv.innerHTML = repoHTML;
        lucide.createIcons();
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GitHubAnalyzer();
});