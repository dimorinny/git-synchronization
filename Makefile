install:
	python3 setup.py install

publish-test:
	python3 setup.py sdist upload -r testpypi