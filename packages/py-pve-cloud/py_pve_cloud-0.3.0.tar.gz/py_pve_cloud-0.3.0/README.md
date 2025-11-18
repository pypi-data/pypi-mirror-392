# py-pve-cloud

this is the core python library package that serves as a foundation for pve cloud.

## alembic orm

this project uses sqlalchemy + alembic integrated into the collection for management of the patroni database schema.

edit `src/orm/alchemy.py` database classes and run `alembic revision --auto-enerate -m "revision description"` from the orm folder, to commit your changes into the general migrations. before you need to do a `pip install .` to get the needed orm pypi packages.

you also need to `export PG_CONN_STR=postgresql+psycopg2://postgres:{{ patroni_postgres_pw }}@{{ proxy or master ip }}:{{ 5000 / 5432 }}/pve_cloud?sslmode=disable` env variable first with a testing database for alembic to work against. to create a new migration the database needs to be on the latest version, run `alembic upgrade head` to upgrade it.

## Releasing to pypi manually

increment the version in pyproject.toml and run `pip install build==1.3.0 twine==6.2.0` and this to release:

```bash
export PYPI_TOKEN= # set pve cloud pypi account access token

rm -rf dist
python3 -m build
python3 -m twine upload dist/*
```

## Developing locally

activate your venv and simply run `pip install -e .` to install this package in edit mode. Any changes will be live.

to deploy the package to the locally hosted pypi `python3 -m twine upload --repository-url http://localhost:8088/ dist/*`

for user and password enter anything you like it doesnt matter.

### Watchdog TDD

activate your python venv with installed pve_cloud collection deps and run `python build-watchdog.py`. This will dynamically build this package to local pypi repo.