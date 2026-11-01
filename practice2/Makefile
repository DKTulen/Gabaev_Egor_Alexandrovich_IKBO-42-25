PYTHON ?= python3

.PHONY: run test demo

run:
	$(PYTHON) src/main.py $(ARGS)

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

demo:
	bash scripts/demo_config.sh
	bash scripts/demo_vfs_min.sh
	bash scripts/demo_vfs_multi.sh
	bash scripts/demo_vfs_deep.sh
	bash scripts/demo_errors.sh
