SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	mypy --explicit-package-bases --namespace-packages platonic
	poetry run flakehell lint platonic tests

.PHONY: unit
unit:
	pytest tests

.PHONY: package
package:
	poetry check
	pip check
	safety check --bare --full-report


.PHONY: format
format:
	poetry run isort -rc platonic tests

.PHONY: test
test: lint unit package
