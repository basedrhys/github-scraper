import time
import requests
import json

class Utils:
    @staticmethod
    def is_target_file(tree_node, config):
        return tree_node['type'] == 'blob' and tree_node['path'].endswith(config.suffix)

    @staticmethod
    def is_subdir(tree_node):
        return tree_node['type'] == 'tree'
    
    @staticmethod
    def get_remaining_tokens(res):
        if 'X-RateLimit-Remaining' in res.headers:
            return int(res.headers['X-RateLimit-Remaining'])
        else:
            return 5000
    
    @staticmethod
    def get_wait_time(res):
        reset_time = res.headers['X-RateLimit-Reset']
        return int(reset_time) - int(time.time())
    
    @staticmethod
    def hit_rate_limit(res):
        return res.status_code == 403 and Utils.get_remaining_tokens(res) == 0
    
    @staticmethod
    def send_github_req(config, endpoint_url, params={}, append_base=False, include_header=False):
        headers = {
        'Authorization': 'token ' + config.token,
        'User-Agent': config.user_agent
        }

        if append_base:
            endpoint_url = config.base_url + endpoint_url
            
        res = requests.get(endpoint_url, params=params, headers=headers)
        
        content = json.loads(res.content)
        
        # Hit the rate limit, poll every 10 seconds until we're good again
        if Utils.hit_rate_limit(res):
            print("Hit rate limit, you may have to wait up to {} seconds".format(Utils.get_wait_time(res)))
            while True:

                rate_url = 'rate_limit'
                rate_res = Utils.send_github_req(rate_url, append_base=True)
        
                tokens = rate_res['resources']['core']['remaining']
#                 print(json.dumps(rate_res, indent=4, sort_keys=True))
            
                if tokens > 0:
                    print("We're good, sending original request again")
                    # Send the request again and stop checking the rate limit
                    res = requests.get(endpoint_url, params=params, headers=headers)
                    break
                
                
                print("Still rate limited, you may have to wait another {} seconds..."
                      .format(Utils.get_wait_time(res)))
                
                time.sleep(10)        
        elif res.status_code != 200:
            print("{} error requesting URL: {}".format(res.status_code, endpoint_url))
            print(json.dumps(content, indent=4, sort_keys=True))
            return content

        
        # Return the results
        if include_header:
            return {
                'content': content,
                'headers': res.headers
            }
        else:
            return content