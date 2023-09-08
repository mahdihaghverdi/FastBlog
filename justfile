default: run-server

export secret_key := 'a'
export algorithm := 'b'

prod-database := 'postgresql+asyncpg://postgres:postgres@0.0.0.0:5432'
test-database := 'sqlite+aiosqlite:///'

run-server $database_url=prod-database:
  uvicorn src.web.app:app --reload

test $database_url=test-database:
  pytest --no-header --no-summary --cov=src --cov-report=html --cov-report=term-missing

migrate message $database_url=prod-database:
  alembic revision --autogenerate -m "{{message}}"

upgrade $database_url=prod-database:
  alembic upgrade head

downgrade $database_url=prod-database:
  alembic downgrade base
