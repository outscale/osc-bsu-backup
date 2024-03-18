PYTHON3=$$(which python3)
PYTHONFILES=$$(find osc_bsu_backup -iname '*.py')
PYTHONUTESTFILES=$$(find tests -iname '*.py')
VERSION=$$(git describe --abbrev=0 --tags)
PWD=$$(pwd)

virtualenv:
	test -d ./venv || $(PYTHON3) -m venv venv

clean:
	rm -rf venv dist build osc_bsu_backup.egg-info

develop: virtualenv
	./venv/bin/pip install -e .

unit: virtualenv format isort mypy develop pylint
	./venv/bin/python -m unittest -f -v $$(ls tests/unit/test_*.py)

integration: virtualenv format isort mypy develop pylint
	./venv/bin/python -m unittest -f -v $$(ls tests/integration/test_*.py)

wheel: virtualenv
	./venv/bin/pip install wheel && ./venv/bin/python setup.py bdist_wheel

pylint: virtualenv
	./venv/bin/pip install pylint && ./venv/bin/pylint --disable=C0111 $(PYTHONFILES) && ./venv/bin/pylint --disable=C0111 $(PYTHONUTESTFILES)

mypy: virtualenv
	./venv/bin/pip install mypy "boto3-stubs[essential]" && ./venv/bin/mypy $(PYTHONFILES)

isort: virtualenv
	./venv/bin/pip install isort && ./venv/bin/isort $(PYTHONFILES) && ./venv/bin/isort $(PYTHONUTESTFILES)

format: virtualenv 
	./venv/bin/pip install black && ./venv/bin/black $(PYTHONFILES) && ./venv/bin/black $(PYTHONUTESTFILES)

docker-image:
	docker build -t osc-bsu-backup:$(VERSION) .

docker-develop: docker-image
	docker run \
		-v $(PWD)/dist:/root/osc-bsu-backup/pkg \
		osc-bsu-backup:$(VERSION) develop

docker-unit: docker-image
	docker run osc-bsu-backup:$(VERSION) unit

docker-integration: docker-image
	docker run \
		-e "AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID)" \
		-e "AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY)" \
		osc-bsu-backup:$(VERSION) integration

docker-wheel: docker-image
	docker run \
		-v $(PWD)/dist:/root/osc-bsu-backup/pkg \
		osc-bsu-backup:$(VERSION) wheel
