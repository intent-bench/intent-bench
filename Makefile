.PHONY: setup test validate run-all analyze charts clean icon lint

SHELL := /bin/bash

# Environment setup
setup:
	pip3 install -r analysis/requirements.txt
	pip3 install pre-commit black flake8 mypy types-PyYAML
	pre-commit install
	@if command -v rsvg-convert >/dev/null 2>&1; then \
		$(MAKE) icon; \
	else \
		echo "Note: rsvg-convert not found, skipping icon build (install librsvg to enable)"; \
	fi
	@echo "Setup complete."

# Lint all code
lint:
	python3 -m black --check --diff .
	python3 -m flake8 .
	python3 -m mypy lib/parse_transcript.py entropy/agent_entropy.py analysis/compare.py analysis/plot.py
	shellcheck -e SC1091 -e SC2034 bench.sh agents/*.sh treatments/*.sh lib/csv.sh scripts/*.sh tests/*.sh

# Validate all experiments (default treatment + manual-spec)
validate:
	@for exp in experiments/*.yaml; do \
		name=$$(basename "$$exp" .yaml); \
		bash bench.sh validate "$$name"; \
	done
	@echo "--- manual-spec treatment ---"
	@for plugin in treatments/*.sh; do \
		name=$$(basename "$$plugin" .sh); \
		if bash "$$plugin" validate 2>/dev/null; then \
			echo "  [PASS] $$name validate"; \
		else \
			echo "  [WARN] $$name validate (runtime deps unavailable)"; \
		fi; \
	done

# Run all experiments (N=5 per condition, default treatment)
run-all:
	@for exp in experiments/*.yaml; do \
		name=$$(basename "$$exp" .yaml); \
		echo "=== $$name ==="; \
		bash bench.sh run "$$name" --condition control --runs 5; \
		bash bench.sh run "$$name" --condition treatment --runs 5; \
	done

# Statistical analysis (copies output into docs/ for GitHub Pages)
analyze:
	python3 analysis/compare.py results/summary.csv
	cp results/analysis.json docs/analysis.json
	cp results/summary.csv docs/summary.csv

# Generate charts
charts:
	python3 analysis/plot.py results/summary.csv

# Generate 256x256 PNG icon from SVG
icon: assets/icon-256.png

assets/icon-256.png: assets/icon.svg
	rsvg-convert -w 256 -h 256 assets/icon.svg -o assets/icon-256.png

# Generate manual-spec fixtures from RTMX fixtures
gen-fixtures:
	bash scripts/gen-manual-spec.sh

# Run tests
test:
	@echo "Running harness tests..."
	bash tests/test_harness.sh
	@echo "Running entropy tests..."
	bash tests/test_entropy.sh

# Initialize empty ledger
init-ledger:
	bash bench.sh init-ledger

# Clean generated artifacts (not results)
clean:
	rm -rf results/charts/*.png results/charts/*.svg assets/icon-256.png
