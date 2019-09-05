from github_scraper.utils import Utils
import re
import os
import base64


class Owner:
    def __init__(self, owner, config):
        self.owner = owner
        self.repos = None
        self.config = config
        
    def get_repos(self, per_page=100):
        # Caching
        if self.repos:
            return self.repos
        else:
            # TODO Support paging through the results
            collected_all = False
            
            # The next link is between angle brackets
            regex = '<(.+)>'
            
            repos = []
            url = 'users/{}/repos'.format(self.owner)
            params = {'per_page': per_page}
            res = Utils.send_github_req(self.config, url, params=params, append_base=True, include_header=True)
            
            while not collected_all:
                # Add all the repos on this page
                for repo in res['content']:
                    repos.append(repo['name'])
                    
                # We need to check if there's more pages to look at
                if 'Link' in res['headers']:
                    link_split = res['headers']['Link'].split(',')
                    for link_rel in link_split:
                        if 'next' in link_rel:
                            # Keep collecting repos if theres a next page
                            m = re.search(regex, link_rel)
                            actual_link = m.group(1)
                            res = Utils.send_github_req(self.config, actual_link, params=params, include_header=True)
                            # Stop checking headers, load the next page
                            collected_all = False
                            break
                        else:
                            # If there was a link in the header but it's not a next link, we're done
                            collected_all = True
                else:
                    # If there's no link in the header, we're done
                    collected_all = True
                
            self.repos = repos    
            return self.repos
    
    def many_target_files(self, repo):
        endpoint = 'repos/{}/{}/languages'.format(self.owner, repo)
        
        res = Utils.send_github_req(self.config, endpoint, append_base=True)
        
        target_bytes = 0
        total_bytes = 1
        thresh = 0.1
        
        keys = res.keys()
        for key in keys:
            if key == self.config.repo_language:
                target_bytes += res[self.config.repo_language]

            total_bytes += res[key]
                
        percent_java = target_bytes / float(total_bytes)
        return percent_java > thresh
        
    def get_default_branch(self, repo):
        url = 'repos/{}/{}'.format(self.owner, repo)
        
        res = Utils.send_github_req(self.config, url, append_base=True)
        
        return res['default_branch']
        
        
    # given a user and repo, download all target files
    def download_repo(self, repo, curr_index=0):
        # First check if this repo has enough Java files to be worth searching
        if not self.many_target_files(repo):
            print("\tIgnoring repo: {} at index {}, not enough target files".format(repo, curr_index))
            return 0
        
        print("Starting repo {} at index {}".format(repo, curr_index))     
        
        # Get the default branch
        default_branch = self.get_default_branch(repo)
        
        # Get the sha for the root of the tree
        url = 'repos/{}/{}/branches/{}'.format(self.owner, repo, default_branch)
        res = Utils.send_github_req(self.config, url, append_base=True)
        
        tree_sha = res['commit']['sha']

        file_count = self.walk_git_tree(repo, tree_sha, 0)
        
        return file_count
    
    def walk_git_tree(self, repo, sha, file_count):
        url = 'repos/{}/{}/git/trees/{}'.format(self.owner, repo, sha)

        results = Utils.send_github_req(self.config, url, append_base=True)

        if 'tree' in results:
            for branch in results['tree']:
                if Utils.is_target_file(branch, self.config):
                    self.download_blob(repo, branch['path'], branch['url'])
                    file_count += 1

                elif Utils.is_subdir(branch):
#                     print("\tExploring branch {}".format(branch['path']))
                    file_count = self.walk_git_tree(repo, branch['sha'], file_count)
                    
        return file_count

    def download_blob(self, repo, name, url):
        res = Utils.send_github_req(self.config, url)

        if 'content' not in res:
            print("ERROR downloading {},{},{},{}.\n{}".format(self.owner, repo, name, url, res))
            return False

        # Make the folder for the file if it doesn't exist
        file_folder = os.path.join(self.config.dataset_dir, self.owner)
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)

        # There may be a file already with this name from the repo, so add a number to differentiate
        file_count = 1
        file_loc = os.path.join(file_folder, '{}__{}_{}'.format(repo, file_count, name))
        while os.path.exists(file_loc):
            file_count += 1
            file_loc = os.path.join(file_folder, '{}__{}_{}'.format(repo, file_count, name))
            
        # Write the content to the file
#         print("Downloading file: {}".format(file_loc))
        with open(file_loc, mode='wb') as new_file:
            content = base64.b64decode(res['content'])
            new_file.write(content)
                
        return True