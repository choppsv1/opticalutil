PIP=pip
PYLINT=pylint -sn -rn --rcfile=.pylintrc
PYTEST=py.test
PYTHON=python

TSFILE=.lint-timestamp

check:
	@echo Running lint on changes with PYLINT=$(PYLINT)
	@OK=YES; for f in $$(git status | awk '/^[ \t]+(modified|new file): +.*.py$$/{print $$2}'); do if [[ $$f -nt $(TSFILE) ]]; then echo "=== $$f"; if ! $(PYLINT) $$f; then OK=NO; fi; fi; done; if [[ $$OK = YES ]]; then touch $(TSFILE); fi

clean:
	find . -name '*.pyc' -exec rm {} +
	$(PYTHON) setup.py clean
	rm -rf bulid doc/build

lint:
	@for f in $$(find opticalutil tests -name '*.py'); do \
		echo "=== Linting $$f"; \
		$(PYLINT) $$f; \
	done

test:	lint run-test

run-test:
	@echo "Running python tests"
	$(PYTEST) -v --doctest-modules

upload:
	python setup.py sdist upload

register:
	python setup.py register
