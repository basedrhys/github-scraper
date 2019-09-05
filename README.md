# github-scraper
Simple python package designed for easy downloading of source code from Github Users.

Terms:
- **Owner** is used to describe a repository owner/user that created the repository. Owner is GitHubs term so it's used here for consistency
## Usage
Downloading all Java files from a GitHub user, 'zxing'

    >>> from file_scraper import FileScraper
    >>> scraper = FileScraper('MY_USERNAME', 'MY_API_TOKEN')
    >>> scraper.download_owner('zxing')
    
    Scraping owner: zxing
    Searching 1 repos, starting from index 0...
    Deleting 0 files first from partially finished repo...
    Starting repo zxing at index 0
    Downloaded 499 total target files