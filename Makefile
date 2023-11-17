
init:
	pip install -r requirements.txt

build:
	python -m build .

install: build
	pip install -e .
