
init:
	pip install -r requirements.txt

build:
	python3 -m build .

install: build
	pip install -e .
