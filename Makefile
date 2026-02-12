.PHONY: api bot upgrade revision

PY := ./.venv/bin/python
ALEMBIC := ./.venv/bin/alembic

api:
	$(PY) -m vira.api

bot:
	$(PY) -m vira.bot

upgrade:
	$(ALEMBIC) upgrade head

revision:
	$(ALEMBIC) revision --autogenerate -m "$(m)"
