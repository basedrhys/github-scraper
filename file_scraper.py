import re
import os
import glob
from utils import Utils
from owner import Owner
from config import Config

class FileScraper:
    def __init__(self, user_agent='', token='', config=None):
        # Create the default config if we just get given a user agent and token
        if config == None:
            if user_agent == '' or token == '':
                print("ERR: You must at least provide a user agent and token for API authentication.")
                return None

            config = Config(user_agent, token)

        self.config = config
    
    def get_tokens_rem(self):
        url = 'rate_limit'
        res = Utils.send_github_req(self.config, url, append_base=True)
        
        return res['resources']['core']['remaining']
    
    def get_top_owners(self, n=10, unique=True):
        repo_addr = 'search/repositories'
        params = {
            'q': '{}+language:{}'.format(config.query_language, config.query_language),
            'per_page': n,
            'sort': 'stars'}

        top_repos = Utils.send_github_req(self.config, repo_addr, params=params, append_base=True)
        items = top_repos['items']
    
        if unique:
            top_owners = []
            for result in items:
                tmp_owner = result['owner']['login']
                if tmp_owner not in top_owners:
                    top_owners.append(tmp_owner)
        else:
            top_owners = [result['owner']['login'] for result in items]

        return top_owners
    
    def download_owner(self, owner, start_index = 0):
        print("Scraping owner: {}".format(owner))
        owner_scraper = Owner(owner, self.config)
        repos = owner_scraper.get_repos()

        print("Searching {} repos, starting from index {}...".format(len(repos), start_index))
        repos = repos[start_index:]
        
        # Delete files from partially finished repo if we're not starting from the start
        start_repo = repos[0]

        file_list = glob.glob(os.path.join(self.config.dataset_dir, owner, start_repo) + "*")
        print("Deleting {} files first from partially finished repo...".format(len(file_list)))

        # Iterate over the list of filepaths & remove each file.
        for file_path in file_list:
            try:
                os.remove(file_path)
            except:
                print("Error while deleting file : ", file_path)
                
        
        file_count = 0
        # For each repo that this owner has, collect the java files
        curr_index = start_index
        for repo in repos:
            file_count += owner_scraper.download_files(repo, curr_index)
            curr_index += 1
            
        print("Downloaded {} total target files".format(file_count))
            
    def download_top_owners(self, n):
        top_owners = self.get_top_owners(n=n)
        print("Downloading java files for top owners:")
        print(top_owners)
        # For each of the top owners
        for owner in top_owners:
            self.download_owner(owner)