# Define phony targets (targets that don't represent files)
.PHONY: help sync install add add-dev remove lock format format-check typecheck \
        build clean deep-clean ci-check rename uml seed demo

# Default target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Dependency Management ---
sync: ## Create venv, resolve lockfile, and install project
	uv sync

install: sync ## Ensure project is installed (runs sync)
	@echo "Project synced and installed successfully."

install-hooks: ## Install pre-commit git hooks (run once after cloning)
	uv run pre-commit install

add: ## Add a new dependency (Usage: make add PKG=requests)
	uv add $(PKG)

add-dev: ## Add a dev dependency (Usage: make add-dev PKG=httpx2)
	uv add --dev $(PKG)

remove: ## Remove a dependency (Usage: make remove PKG=requests)
	uv remove $(PKG)

lock: ## Update the lockfile without installing to the venv
	uv lock

# --- Code Quality ---
format: ## Format code locally (mutates files)
	uv run ruff format .
	uv run ruff check --fix .

format-check: ## Check formatting without mutating (for CI)
	uv run ruff format --check .
	uv run ruff check .

typecheck: ## Run mypy type checking
	uv run mypy .

# --- CI/CD ---
ci-check: format-check typecheck ## Run all CI checks locally (non-mutating, enforces 80% coverage)

# --- Maintenance ---
clean: ## Clean up caches and build artifacts (keeps .venv intact)
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	uv cache clean

clean-venv: ## Remove the virtual environment
	rm -rf .venv
	@echo "Virtual environment removed. Run 'make install' to recreate it."

deep-clean: clean ## Nuclear clean: removes logs, context file, and lockfile
	rm -rf logs/
	rm -f uv.lock
	@echo "Deep clean complete. (Next 'make install' will re-resolve dependencies)"

# --- Packaging ---
build: ## Build wheel + sdist
	uv build

rename: ## Rename project (Usage: make rename NEW_NAME=my_app NEW_PROJECT=my-app)
	@if [ -z "$(NEW_NAME)" ] || [ -z "$(NEW_PROJECT)" ]; then \
		echo "Usage: make rename NEW_NAME=my_app NEW_PROJECT=my-app"; exit 1; fi
	@uv run python - "$(NEW_NAME)" "$(NEW_PROJECT)" <<'PY'
	import pathlib, re, sys
	pkg, prj = sys.argv[1], sys.argv[2]
	assert re.fullmatch(r"[a-z_][a-z0-9_]*", pkg), "NEW_NAME must be a valid Python identifier"
	for old, new in [("src/tpp_mizan", f"src/{pkg}"), ("tests/tpp_mizan", f"tests/{pkg}")]:
	    if pathlib.Path(old).exists():
	        pathlib.Path(old).rename(new)
	# Added '.gitignore' to ensure the context file exclusion is also renamed
	for ext in ("*.py", "*.toml", "*.yaml", "*.md", "Makefile", "*.yml", ".gitignore"):
	    for p in pathlib.Path(".").rglob(ext):
	        if any(x in p.parts for x in (".venv", ".git", "logs", ".pytest_cache", ".mypy_cache", ".ruff_cache")):
	            continue
	        p.write_text(p.read_text().replace("tpp_mizan", pkg).replace("tpp-mizan", prj))
	PY
	@echo "✅ Rename complete! Run 'make deep-clean && make install' to rebuild."

uml: ## Generate UML model
	uv run pyreverse -o mmd -p retrofun src/retrofun

seed:                   ## DESTRUCTIVE: drop + create + load
	uv run python -m retrofun.import_products

demo:
	uv run python -m retrofun.main