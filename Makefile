
init:
	pip install -r requirements.txt

build:
	python3 -m build .

lint:
	pylint `git ls-files *.py`


install: build
	pip install -e .
