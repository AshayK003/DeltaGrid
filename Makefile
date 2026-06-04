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
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=1) for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -rf .pytest_cache .mypy_cache .ruff_cache
