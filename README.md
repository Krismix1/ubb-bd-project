How to run:

- Install [`poetry`](https://github.com/python-poetry/poetry#installation) and [`pyenv`](https://github.com/pyenv/pyenv)
- `pyenv install 3.10.8`
- `pyenv local 3.10.8`
- `poetry install`
- `docker-compose up -d` to spin up kafka and Spark
- Activate Poetry virtual environment using `poetry shell`
- Run `python project/importer.py` to start ingesting data
- Open another terminal, activate Poetry venv, and run `python project/kafka_consumer.py`

