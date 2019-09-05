class Config:
    def __init__(self, user_agent, token, repo_language='Java', query_language='java', suffix='.java', 
                 base_url = 'https://api.github.com/', dataset_dir='github_files'):
        self.user_agent = user_agent
        self.token = token
        self.dataset_dir = dataset_dir
        self.repo_language = repo_language
        self.query_language = query_language
        self.suffix = suffix
        self.base_url = base_url