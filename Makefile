.PHONY: setup test validate run-all analyze charts clean icon

SHELL := /bin/bash

# Environment setup
setup: icon
	pip3 install -r analysis/requirements.txt
	@echo "Setup complete."

# Validate all experiments
validate:
	@for exp in experiments/*.yaml; do \
		name=$$(basename "$$exp" .yaml); \
		bash bench.sh validate "$$name"; \
	done

# Run all experiments (N=5 per condition, default treatment)
run-all:
	@for exp in experiments/*.yaml; do \
		name=$$(basename "$$exp" .yaml); \
		echo "=== $$name ==="; \
		bash bench.sh run "$$name" --condition control --runs 5; \
		bash bench.sh run "$$name" --condition treatment --runs 5; \
	done

# Statistical analysis
analyze:
	python3 analysis/compare.py results/summary.csv

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
