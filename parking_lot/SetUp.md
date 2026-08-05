- Use virtual environment to create venv into the current folder
```bash
source .venv/bin/activate
```
- install python packages
```bash
pip install -r requirements.txt
```

- copy `.env.example` to `.env` and update the connection string for your environment
```bash
cp .env.example .env
```

- run via below command to start the application

```bash
.venv/bin/python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Open the API docs at http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc