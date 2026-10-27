# Publishing notes to the portfolio

Markdown committed and pushed to `main` under `04 Knowledge/` or `02 Projects/` appears automatically in [the portfolio articles](https://chheng-lydiya-portfolio.vercel.app/#/articles).

1. Write a `.md` note in either folder and add any diagrams to Git.
2. Commit and push to `main` as usual.
3. The **Publish portfolio articles** GitHub Action builds `articles.json` on the dedicated `portfolio-articles` branch. The website reads that feed; no portfolio deployment is needed. Allow the workflow and GitHub's raw-content cache a few minutes, then refresh Articles.

The workflow uses only committed files. Daily notes, Inbox, templates, root dashboards, application settings, notebooks, PDFs, README/index files and Excalidraw source Markdown are not published as articles. Images/PDFs linked from an included article remain accessible through their repository URLs. Do not put private material in the public repository.

The filename supplies the title unless a top-level `# Title` is present. Creation/update dates come from Git history. Article URLs are based on the file path and remain stable while the note's content changes; renaming a file changes its URL. Deleting a note removes it from the next feed.

Optional frontmatter supports simple single-line values and comma-separated inline tags:

```yaml
---
title: My robot build
excerpt: What I learned while building the drive system.
tags: [Robotics, Control]
publish: true
---
```

Set `draft: true` or `publish: false` to exclude a note. This controls the portfolio feed only; the source file remains visible in the public GitHub repository. Obsidian `![[image.png]]` embeds and `[[Note|label]]` links are converted for the website. Diagrams use the exact source commit; published-note links open the portfolio article. Missing or ambiguous links remain readable text. Code examples are preserved.

GitHub notes are edited in this repository. Article Studio continues to manage its own publications separately. The exporter and workflow are in `.github/scripts/` and `.github/workflows/portfolio-articles.yml`. To verify locally:

```sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py'
python3 .github/scripts/export_portfolio_articles.py /tmp/portfolio-articles.json
```
