.PHONY: install lint typecheck test serve clean

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

lint:
	ruff check src/ app/

typecheck:
	mypy src/ app/

test:
	pytest tests/ -v

serve:
	streamlit run app/main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
