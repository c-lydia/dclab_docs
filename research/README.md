# Research and References

Research notes and supporting references for robotics and localization.

## Localization

| Topic | Materials |
|---|---|
| FAST-LIO2 | [Notes](localization/Fast%20LIO%202.md) · [PDF](localization/Fast%20LIO%202.pdf) |
| Livox MID-360 localization | [Notes](localization/Localization%20with%20Livox%20MID-360%203D%20LiDAR.md) · [PDF](localization/Localization%20with%20Livox%20MID-360%203D%20LiDAR.pdf) |
| Monte Carlo localization | [Paper](localization/reference/monte-carlo-localization.pdf) |

Additional localization papers are in the
[localization/reference](localization/reference/) directory.

## General references

- [Principles of Robot Autonomy](references/principles-of-robot-autonomy.pdf)
- [Making Embedded Systems (2011)](references/Elecia%20White%20-%20O%27Reilly%20Making%20Embedded%20Systems%20%282011%29.pdf)

## Adding research notes

### Selected portfolio studies

- [FAST-LIO2 — Understanding LiDAR–Inertial Odometry](portfolio/FAST-LIO2%20Study.md)
- [Localization with Livox MID-360 — A Study of the Options](portfolio/Livox%20MID-360%20Localization%20Study.md)

These focused editions appear in the portfolio with the **Research & Study Notes** tag. They explain the reading and its limitations without robot-specific implementation code. Edit these editions to update their portfolio articles; the original localization notes remain outside the feed.

Research Markdown must explicitly set `publish: true` in frontmatter to enter the feed. Setting `draft: true`, setting `publish: false`, or removing the opt-in excludes it on the next run. Reference folders (`reference/` and `references/`), PDFs, and README/index files are always excluded. Unfinished studies should stay without the opt-in.

Commit and push publication changes to `portfolio-publications`; the **Publish portfolio articles** workflow writes `articles.json` on that same branch. The live portfolio reads that branch, and source links open its Markdown files. Do not merge portfolio publication changes into `main`. No portfolio deployment is needed for later article edits. The old `portfolio-articles` feed is no longer the website's source. Check changes locally with:

```sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py'
python3 .github/scripts/export_portfolio_articles.py /tmp/portfolio-articles.json
```

### Working notes

Record the source, research question, assumptions, method, and findings.
Distinguish published results from observations made during lab experiments.

Use the [research note template](../templates/notes/Research.md) for new
entries.

[Back to the repository guide](../README.md)
