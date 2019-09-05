# github-scraper
Simple python package designed for easy downloading of source code from Github Users.

Terms:
- **Owner** is used to describe a repository owner/user that created the repository. Owner is GitHubs term so it's used here for consistency

## Installation
    python3 -m pip install github_scraper

## Usage
Import and set up the config with username and API token

    >>> import github_scraper as gs
    >>> config = gs.Config('MY_USERNAME', 'MY_API_KEY')

It defaults to downloading Java files, but can be configured for other languages

    >>> config = gs.Config('MY_USERNAME', 'MY_API_KEY', repo_language='Python', query_language='python', suffix='.py')

Downloading all Java files from myself

    >>> scraper = gs.FileScraper(config)
    >>> scraper.download_owner('basedrhys')
    Scraping owner: basedrhys
    ...

Downloading all Java files from a specific repo

    >>> owner = gs.Owner('google', config)
    >>> owner.download_repo('tink')
