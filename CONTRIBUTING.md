# Maintaining the documentation

## File placement

- Put course notes and their images, slides, and exports together under `courses/<topic>/`.
- Put project plans and toolchain guides under `projects/`.
- Put research notes and papers under `research/`; localization papers belong in `research/localization/reference/`.
- Put Jupyter notebooks under `notebooks/` and update their Colab links after a move.
- Keep reusable slide/note templates under `templates/` and Excalidraw libraries under `assets/diagram-libraries/`.
- Keep historical bundles under `archive/` only when they contain material not represented by current files.

Use lowercase folder names with hyphens between words. Existing document titles remain descriptive. Use relative Markdown links and images so GitHub renders them; percent-encode spaces and parentheses in link destinations. Keep Python caches, virtual environments, editor lock files, KiCad local state, and Underlight sync metadata out of Git.

## Publishing

Follow [PORTFOLIO.md](PORTFOLIO.md) for automatic publication of course and project notes. README/index files, templates, research, archives, and notebooks are excluded from the feed. Existing portfolio path aliases in the exporter preserve article URLs across this folder reorganization; retain those aliases.

## Checks

Run from the repository root:

```sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py'
python3 .github/scripts/export_portfolio_articles.py /tmp/portfolio-articles.json
git diff --check
```

Stage new or moved files before exporting: the exporter selects files using Git's tracked-file list. Before committing a move, check relative links, notebook Colab badges, and portfolio output. Review PDFs/slides separately when regenerating them; editing Markdown does not regenerate those exports.
