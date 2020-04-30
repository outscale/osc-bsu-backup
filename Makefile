PYTHON3=$$(which python3)
PYTHONFILES=$$(find osc_bsu_backup -iname '*.py')
PYTHONUTESTFILES=$$(find tests -iname '*.py')
VERSION=$$(git describe --abbrev=0 --tags)
PWD=$$(pwd)

virtualenv:
	$(PYTHON3) -m venv venv

clean:
	rm -rf venv dist build osc_bsu_backup.egg-info

develop: virtualenv
	./venv/bin/python setup.py develop

unit: virtualenv format develop
	./venv/bin/python -m unittest -v $$(ls tests/unit/test_*.py)

integration: virtualenv format develop
	./venv/bin/python -m unittest -v $$(ls tests/integration/test_*.py)

wheel: virtualenv
	./venv/bin/pip install wheel && ./venv/bin/python setup.py bdist_wheel

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
	docker run osc-bsu-backup:$(VERSION) integration

docker-wheel: docker-image
	docker run \
		-v $(PWD)/dist:/root/osc-bsu-backup/pkg \
		osc-bsu-backup:$(VERSION) wheel
