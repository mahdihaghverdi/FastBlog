default: run-server

export secret_key := 'a30de51667c19a70a5c098f4dea65d23d4884340bca29e854c1becfbe1a49de1'

prod-database := 'postgresql+asyncpg://postgres:postgres@0.0.0.0:5432'
test-database := 'sqlite+aiosqlite:///'

run-server $database_url=prod-database:
  uvicorn src.web.app:app --reload

database:
  docker run \
    --name psql-dev \
    --rm \
    --detach \
    --env POSTGRES_USER=postgres \
    --env POSTGRES_PASSWORD=postgres \
    --env POSTGRES_DB=fastblog_db \
    -p 5432:5432 \
    -v fastblog-data:/var/lib/postgresql/data \
     postgres

enter-database:
  docker exec -it psql-dev psql -U postgres

test $database_url=test-database:
  pytest --durations=5 --no-header --cov=src --cov-report=html --cov-report=term-missing tests

test-no-cov $database_url=test-database:
  pytest --durations=5 --no-header tests

test-spec where $database_url=test-database:
  pytest --durations=5 --no-header --cov=src --cov-report=html --cov-report=term-missing tests/{{where}}

test-spec-no-cov where $database_url=test-database:
  pytest --durations=5 --no-header tests/{{where}}

migrate message $database_url=prod-database:
  alembic revision --autogenerate -m "{{message}}"

upgrade $database_url=prod-database:
  alembic upgrade head

downgrade $database_url=prod-database:
  alembic downgrade base
