FROM python:3

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir poetry
RUN poetry install

COPY . .

CMD [ "poetry", "run", "gunicorn", "-b 0.0.0.0:8000", "web:app"]
