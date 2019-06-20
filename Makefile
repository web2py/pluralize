clean:
	rm -rf dist
build:
	make clean
	python3 setup.py build
install: build
	python3 setup.py install
test:	install
	python3 -m unittest tests.test_simple
deploy:
	make clean
	#http://guide.python-distribute.org/creation.html
	python setup.py sdist
	twine upload dist/*
