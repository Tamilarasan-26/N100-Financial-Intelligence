.PHONY: install load ratios test report dashboard api clean

install:
	pip install -r requirements.txt

load:
	python src/etl/loader.py
	python src/etl/validator.py
	python src/etl/quarantine.py
	python src/etl/create_validated_data.py
	python src/etl/db_loader.py
	python src/etl/verify_database.py

ratios:
	@echo "Ratio pipeline is scheduled for a future sprint."

test:
	pytest tests/etl -v

report:
	@echo "Report generation is scheduled for a future sprint."

dashboard:
	@echo "Dashboard is scheduled for a future sprint."

api:
	@echo "API is scheduled for a future sprint."

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	python -c "import shutil; shutil.rmtree('.pytest_cache', ignore_errors=True)"