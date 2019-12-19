PYTHON3=$$(which python3)

virtualenv:
	test -f ./venv || \\
		$(PYTHON3) -m venv venv

develop: virtualenv
	./venv/bin/python setup.py develop
