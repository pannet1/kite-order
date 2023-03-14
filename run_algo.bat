@echo on
cmd /k "cd /d E:\py\venv\Scripts & .\activate & cd /d E:\py\venv\dealer-web\dealer_web & uvicorn main:app --reload"
