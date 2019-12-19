PYTHON3=$$(which python3)
PYTHONFILES=$$(find osc_bsu_backup -iname '*.py')

virtualenv:
	$(PYTHON3) -m venv venv

develop: virtualenv
	./venv/bin/python setup.py develop

format: virtualenv
	./venv/bin/pip install black && ./venv/bin/black $(PYTHONFILES)
