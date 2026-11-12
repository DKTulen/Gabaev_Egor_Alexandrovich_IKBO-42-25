PYTHON ?= python3
CONFIG ?= config.yaml

.PHONY: run test demo

run:
	$(PYTHON) src/main.py $(CONFIG)

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

demo:
	$(PYTHON) src/main.py examples/test_acyclic.yaml
