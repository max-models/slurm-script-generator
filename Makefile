# README (Quarto) and the documentation site (docs/, Astro + Starlight).
# Notebook tool: starlight-notebooks, from @max-models/starlight-theme (docs/node_modules).
PYTHON ?= .venv/bin/python
DOCS_ENV = DOCS_PYTHON=$(abspath $(PYTHON))
NOTEBOOKS = cd docs && $(DOCS_ENV) npx starlight-notebooks
FORCE ?=

.PHONY: help readme docs-install docs-cli docs-notebooks docs-dev docs-build docs-preview docs-clean

help:  ## list the targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

readme:  ## render README.md from README.qmd with quarto
	PATH=$(abspath $(dir $(PYTHON))):$$PATH quarto render README.qmd --to gfm

docs-install:  ## Python docs extra and the npm packages
	$(PYTHON) -m pip install -e ".[docs]"
	cd docs && npm ci

# The CLI page runs its examples with Quarto (knitr), in a scratch directory for the files they
# write; the Quarto-only front matter (from `engine:` to `variant:`) is left out of the page.
docs-cli:  ## run the examples of docs/cli/*.qmd into docs/src/content/docs/cli/ (needs quarto and R)
	@tmp=$$(mktemp -d) && for qmd in docs/cli/*.qmd; do \
		name=$$(basename $$qmd .qmd); \
		cp $$qmd $$tmp/ && (cd $$tmp && PATH=$(abspath $(dir $(PYTHON))):$$PATH quarto render $$name.qmd --quiet) || exit 1; \
		awk -v src="$$qmd" '/^engine:/ { skip = 1 } skip && /^---$$/ { skip = 0 } !skip { print } \
			/^---$$/ && ++n == 2 { print "\n<!-- Generated from " src " by `make docs-cli`: edit that file instead. -->" }' \
			$$tmp/$$name.md > docs/src/content/docs/cli/$$name.md; \
		echo "wrote docs/src/content/docs/cli/$$name.md"; \
	done; rm -rf $$tmp

docs-notebooks:  ## execute the changed tutorials and convert all of them (FORCE=1 reruns all)
	$(NOTEBOOKS) execute $(if $(FORCE),--force,)
	$(NOTEBOOKS) convert

docs-dev:  ## live preview at http://localhost:4321/slurm-script-generator/
	$(NOTEBOOKS) convert
	cd docs && $(DOCS_ENV) DOCS_VALIDATE_LINKS=false npx astro dev

docs-build:  ## the static site in docs/dist, as in CI
	$(NOTEBOOKS) convert
	cd docs && npx starlight-check-mdx && $(DOCS_ENV) npx astro build

docs-preview:  ## serve docs/dist
	cd docs && npx astro preview

docs-clean:  ## remove generated pages, assets and build output
	$(NOTEBOOKS) clean
	rm -rf docs/dist docs/.astro
