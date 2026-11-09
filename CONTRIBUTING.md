# Contributing to DCLab Documentation

Contributions should support the lab's teaching, research, or robotics projects.
For the repository-wide orientation, start with the [main
README](README.md).

## Where files belong

| Material | Location |
|---|---|
| Lessons, slides, and course diagrams | [`courses/<topic>/`](courses/) |
| Technical project guides and setup instructions | [`projects/`](projects/) |
| Research notes and reference papers | [`research/`](research/) |
| Jupyter notebooks | [`notebooks/`](notebooks/) |
| Robot schematics | [`hardware/schematics/`](hardware/schematics/) |
| Reusable teaching and technical note templates | [`templates/`](templates/) |
| Excalidraw libraries | [`assets/diagram-libraries/`](assets/diagram-libraries/) |
| Historical course bundles | [`archive/course-bundles/`](archive/course-bundles/) |

Keep each lesson's source files and supporting images together.

## Writing and naming

- Use descriptive filenames.
- Use lowercase folder names with hyphens between words.
- Explain prerequisites before presenting an exercise.
- Include units, assumptions, and hardware or software versions where relevant.
- Use relative Markdown links for files within this repository, and verify that
  each target exists.
- Preserve author credits and cite external sources.
- Keep personal plans, contact details, and private workspace files outside
  this repository.

## Before submitting

- Check that links and images open correctly on GitHub, including links with
  spaces or parentheses in their filenames.
- Update the relevant [README](README.md) when adding, moving, or removing
  files.
- Update notebook [Colab links](https://colab.research.google.com/) when moving
  notebooks.
- Check that example commands match the documented setup.
- Refresh PDF and slide exports when their source material changes.
- Exclude caches, virtual environments, editor settings, and temporary files
  using the repository's [`.gitignore`](.gitignore).

Editing Markdown does not automatically regenerate PDFs or slides.

## Submitting changes

1. Create a branch for your changes, following GitHub's
   [branching guidance](https://docs.github.com/en/get-started/learning-to-code/getting-started-with-git).
2. Edit the relevant files and review the diff.
3. Commit with a concise message describing what changed.
4. Open a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests)
   explaining the change and how you checked it.

You can edit through [GitHub](https://github.com/c-lydia/dclab_docs),
[github.dev](https://github.dev/), or a local checkout.
