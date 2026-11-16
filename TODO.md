# RetroFun TODOS

1. test suit
2. logging
3. UML model *Done*
   - [x] Find a better model-diagram tool than PyUML
     - **Chosen:** pyreverse via `make uml` — renders inheritance, uses import-path names.
     - **Limits:** omits external bases (DeclarativeBase), no association multiplicity, shows raw `Mapped[...]` annotations, includes non-model classes (Settings).
     - **Therefore:** generated diagram = class inventory; docs/models.md keeps the hand-written design diagram with the SQLAlchemy root and the 1 → 0..* association.
