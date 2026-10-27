"""Publish the generated JSON on a dedicated branch using the Actions token."""
import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

repository = os.environ['GITHUB_REPOSITORY']
branch = 'portfolio-articles'

def api(path, method='GET', payload=None):
    request = Request(f'https://api.github.com/repos/{repository}/{path}',
        data=None if payload is None else json.dumps(payload).encode(), method=method,
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2022-11-28',
                 'User-Agent': 'dclab-portfolio-feed'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)

try:
    api(f'git/ref/heads/{branch}')
except HTTPError as error:
    if error.code != 404:
        raise
    api('git/refs', 'POST', {'ref': 'refs/heads/' + branch, 'sha': os.environ['GITHUB_SHA']})

body = Path(sys.argv[1]).read_bytes()
payload = {'message': 'Update portfolio articles from ' + os.environ['GITHUB_SHA'][:12],
           'branch': branch, 'content': base64.b64encode(body).decode()}
try:
    current = api(f'contents/articles.json?ref={branch}')
    if base64.b64decode(current['content']) == body:
        print('Article feed is already current.')
        sys.exit(0)
    payload['sha'] = current['sha']
except HTTPError as error:
    if error.code != 404:
        raise
api('contents/articles.json', 'PUT', payload)
print('Published articles.json on portfolio-articles.')
