# Contributing to DCLab Documentation

Contributions should support the lab's teaching, research, or robotics projects.

## Where files belong

| Material | Location |
|---|---|
| Lessons, slides, and course diagrams | courses/<topic>/ |
| Technical project guides and setup instructions | projects/ |
| Research notes and reference papers | research/ |
| Jupyter notebooks | notebooks/ |
| Robot schematics | hardware/schematics/ |
| Reusable teaching and technical note templates | templates/ |
| Excalidraw libraries | assets/diagram-libraries/ |
| Historical course bundles | archive/course-bundles/ |

Keep each lesson's source files and supporting images together.

## Writing and naming

- Use descriptive filenames.
- Use lowercase folder names with hyphens between words.
- Explain prerequisites before presenting an exercise.
- Include units, assumptions, and hardware or software versions where relevant.
- Use relative Markdown links for files within this repository.
- Preserve author credits and cite external sources.
- Keep personal plans, contact details, and private workspace files outside
  this repository.

## Before submitting

- Check that links and images open correctly on GitHub.
- Update the relevant README when adding, moving, or removing files.
- Update notebook Colab links when moving notebooks.
- Check that example commands match the documented setup.
- Refresh PDF and slide exports when their source material changes.
- Exclude caches, virtual environments, editor settings, and temporary files.

Editing Markdown does not automatically regenerate PDFs or slides.

## Submitting changes

1. Create a branch for your changes.
2. Edit the relevant files and review the diff.
3. Commit with a message describing what changed.
4. Open a pull request explaining the change and how you checked it.

You can edit through GitHub, github.dev, or a local checkout.
