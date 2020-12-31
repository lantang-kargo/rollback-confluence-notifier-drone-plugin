# rollback-confluence-notifier-drone-plugin

## Usage

```
- name: rollback-notes-to-confluence
  image: lstama/rollback-confluence-drone
  failure: ignore
  when:
    event:
      - tag
    ref:
      - refs/tags/*-[Rr][Oo][Ll][Ll][Bb][Aa][Cc][Kk]
  settings:
    GITHUB_USER:
      from_secret: GITHUB_USER
    GITHUB_TOKEN:
      from_secret: GITHUB_TOKEN
    CONFLUENCE_USER:
      from_secret: CONFLUENCE_USER
    CONFLUENCE_TOKEN:
      from_secret: CONFLUENCE_TOKEN
    CONFLUENCE_ORG_ID: your_confluence_org_id (https://<this_one>.atlassian.net)
    CONFLUENCE_DOC_ID: 123456789
```
