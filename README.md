# DCLab robotics documentation

Course notes, practical notebooks, project plans, and research references for robotics, embedded systems, and control.

## Start here

- **Learn electronics and embedded control:** follow the [course guide](courses/README.md).
- **Practice Linux and ROS 2:** open the [notebooks](notebooks/README.md).
- **Set up a project:** see [project plans and toolchains](projects/README.md).
- **Study localization:** see the [research guide](research/README.md).

## Repository layout

| Folder | Contents |
| --- | --- |
| [courses](courses/README.md) | MCU/PWM, power and ADC, DC motor drive, and embedded software lessons; associated slides and diagrams |
| [projects](projects/README.md) | Control-system roadmap, STM32 toolchain setup, and engineering practice plan |
| [research](research/README.md) | LiDAR localization notes, papers, and reference books |
| [notebooks](notebooks/README.md) | Jupyter notebooks for electronics, operating systems, and ROS 2 |
| [hardware/schematics](hardware/schematics) | KiCad robot project and schematic |
| [templates](templates/README.md) | Editable teaching slides and Markdown note templates |
| [assets/diagram-libraries](assets/diagram-libraries) | Excalidraw libraries for circuits, robotics, and software diagrams |
| [guides](guides) | Optional Underlight/Obsidian workspace guidance |
| [archive/course-bundles](archive/course-bundles/README.md) | Historical course ZIPs that differ from the current lesson folders |
| [skills](skills) | Existing workflow instructions |

Markdown notes are the editable lesson text. PDFs are reading/printing exports; PPTX/POTX files are editable slide decks and templates. Keep each lesson's diagrams beside its source. Historical ZIP bundles are not the current course source.

## Editing and publishing

See [CONTRIBUTING.md](CONTRIBUTING.md) for file placement and checks. Notes under `courses/` and `projects/` can appear automatically on the portfolio after a push to `main`; [PORTFOLIO.md](PORTFOLIO.md) explains publishing and opt-outs.

The folder cleanup replaces `02 Projects` with `projects`, `03 Research` with `research`, and the old `04 Knowledge/dclab` collection with topic folders under `courses`, `hardware`, and `templates`. Note templates now live in `templates/notes`. Existing portfolio article IDs and URLs are preserved by the exporter.

## License

See [LICENSE](LICENSE). Third-party references and assets retain their respective notices and licenses.
