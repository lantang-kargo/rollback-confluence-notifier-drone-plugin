# This script is used to add new rollback data on the "Release Rollback Tracker" document.
# Writer: Noviar Endru Ferguson <https://github.com/endru-kargo>

import datetime
import os
import pytz
import requests
import sys

REPOSITORY = os.environ['DRONE_REPO_NAME']
FULL_REPOSITORY = os.environ['DRONE_REPO']
TAG_VERSION = os.environ['DRONE_TAG']

if not TAG_VERSION.lower().endswith('-rollback'):
    sys.stderr.write('Error: Tag version must end with "-rollback"\n')
    quit()

GITHUB_USER = os.environ['PLUGIN_GITHUB_USER']
GITHUB_TOKEN = os.environ['PLUGIN_GITHUB_TOKEN']
GITHUB_URL = 'https://api.github.com/repos/' + FULL_REPOSITORY
CONFLUENCE_USER = os.environ['PLUGIN_CONFLUENCE_USER']
CONFLUENCE_TOKEN = os.environ['PLUGIN_CONFLUENCE_TOKEN']
CONFLUENCE_ORG_ID = os.environ['PLUGIN_CONFLUENCE_ORG_ID']
CONFLUENCE_DOC_ID = os.environ['PLUGIN_CONFLUENCE_DOC_ID']
CONFLUENCE_URL = 'https://' + CONFLUENCE_ORG_ID + '.atlassian.net/wiki/rest/api/content/' + CONFLUENCE_DOC_ID
ROW_ITEM = '<tr><td><p><time datetime="{rollback_date}"/></p></td><td><p>{repository}</p></td><td><p>{tag_version}</p></td><td><p>{rollback_reason}</p></td></tr>'

rollback_date = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d')
rollback_reason = 'N/A'

# Get tag sha
response = requests.get('{url}/git/ref/tags/{tag_version}'.format(url=GITHUB_URL, tag_version=TAG_VERSION), auth=(GITHUB_USER, GITHUB_TOKEN))
if response.status_code != 200:
    sys.stderr.write('Error: Tag not found\n')
    quit()
json_response = response.json()
tag_sha = json_response['object']['sha']

# Get tag info
response = requests.get('{url}/git/tags/{tag_sha}'.format(url=GITHUB_URL, tag_sha=tag_sha), auth=(GITHUB_USER, GITHUB_TOKEN))
if response.status_code == 200:
    # Developer created the tag using annotated tag.
    # Get rollback reason from the tag message.
    json_response = response.json()
    rollback_reason = json_response['message'].strip()
else:
    # It could be that the developer created the tag using Github release UI.
    # Get release info.
    response = requests.get('{url}/releases/tags/{tag_version}'.format(url=GITHUB_URL, tag_version=TAG_VERSION), auth=(GITHUB_USER, GITHUB_TOKEN))
    if response.status_code == 200:
        # Yes, developer created the tag using Github release UI.
        # Get rollback reason from the release body.
        json_response = response.json()
        rollback_reason = json_response['body'].strip()

# Get current Confluence document version, title and content
response = requests.get(CONFLUENCE_URL + '?expand=body.storage,version', auth=(CONFLUENCE_USER, CONFLUENCE_TOKEN))
response.raise_for_status()
json_response = response.json()
version = json_response['version']['number']
title = json_response['title']
content = json_response['body']['storage']['value']

# Add new row to the content
closing_tbody_index = content.find('</tbody>')
content_first_part = content[:closing_tbody_index]
content_last_part = content[closing_tbody_index:]
new_row = ROW_ITEM.format(rollback_date=rollback_date, repository=REPOSITORY, tag_version=TAG_VERSION, rollback_reason=rollback_reason)
new_content = content_first_part + new_row + content_last_part

# Send the updated content
data = {
    'id': CONFLUENCE_DOC_ID,
    'type': 'page',
    'title': title,
    'body': {
        'storage': {
            'value': new_content,
            'representation': 'storage'
        }
    },
    'version': {
        'number': version + 1
    }
}
response = requests.put(CONFLUENCE_URL, json=data, auth=(CONFLUENCE_USER, CONFLUENCE_TOKEN))
response.raise_for_status()
