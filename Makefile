help:
	cat Makefile

testpypi: dist
	twine upload --repository testpypi dist/*

pypi: dist
	twine upload --repository pypi dist/*

dist: build
	python setup.py sdist bdist_wheel

build: clean
	python setup.py build install

clean:
	rm -fr build dist __pycache__ *.egg-info/
