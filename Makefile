test:
	pep8 main.py
	pylint --disable locally-disabled main.py
