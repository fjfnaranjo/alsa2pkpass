.PHONY: black
black:
	@black setup.py alsa2pkpass

.PHONY: test
test:
	@pytest

.PHONY: test-cov
test-cov:
	@pytest --cov=alsa2pkpass --cov-report html
