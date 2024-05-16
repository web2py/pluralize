.PHONY: clean test build deploy

clean:
	rm -rf dist build

test:
	python -m unittest tests/test*.py

build: clean
	python -m build

deploy: build
	python -m twine upload dist/*
