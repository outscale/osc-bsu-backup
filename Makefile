PYTHON3=$$(which python3)
PYTHONFILES=$$(find osc_bsu_backup -iname '*.py')
PYTHONUTESTFILES=$$(find tests -iname '*.py')

virtualenv:
	$(PYTHON3) -m venv venv

develop: virtualenv
	./venv/bin/python setup.py develop

unit: virtualenv format
	./venv/bin/python -m unittest -v $$(ls tests/unit/test_*.py)

integration: virtualenv format
	./venv/bin/python -m unittest -v $$(ls tests/integration/test_*.py)

wheel: virtualenv
	./venv/bin/pip install wheel && ./venv/bin/python setup.py bdist_wheel

format: virtualenv 
	./venv/bin/pip install black && ./venv/bin/black $(PYTHONFILES) && ./venv/bin/black $(PYTHONUTESTFILES)
