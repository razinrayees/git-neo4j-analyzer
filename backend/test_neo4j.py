from fetch_github import fetch_user_data

try:
    data = fetch_user_data('octocat')
    print(f'✅ GitHub API working! Found user: {data["user"]["login"]}')
except Exception as e:
    print(f'❌ GitHub API failed: {e}')