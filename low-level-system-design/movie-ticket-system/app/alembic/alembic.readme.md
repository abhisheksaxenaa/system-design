Generate the first migration:

```bash
alembic revision --autogenerate -m "create initial schema"

Under directory app/alembic
python3 -m alembic -c alembic/alembic.ini revision --autogenerate -m "create initial schema"
```

Review it and then run:
```bash
alembic upgrade head
```
These commands correspond to Alembic's metadata-diff/autogeneration workflow.
