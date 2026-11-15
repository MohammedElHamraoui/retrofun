- test suit
- logging
- UML model
- [x] Find a better model-diagram tool than PyUML
  - **Why:** hides relationships (8 hidden), names classes by file path
    (`src.retrofun.models.product`) instead of import path, shows `Mapped[int]`
    rather than column types.
  - **Keep PyUML for:** quick "does my structure look silly?" checks — it's what  exposed the empty `RetroFunBase` layer.
  - **Try:** `pyreverse -o mmd -p retrofun src/retrofun` (ships with pylint,
    resolves inheritance properly, Mermaid output = no graphviz needed).
  - **Fallback:** hand-written Mermaid `classDiagram` in `docs/models.md`.
  - **Done when:** the diagram shows the full chain
    `DeclarativeBase → Base → BaseEntity → RetroFunBase → Product`
    and renders on GitHub.