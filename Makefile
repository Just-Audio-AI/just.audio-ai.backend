.PHONY: migrate-apply
migrate-apply: ## apply alembic migrations to database/schema
	alembic upgrade head

.PHONY: migrate-create
migrate-create:  ## Create new alembic database migration aka database revision.
	alembic revision --autogenerate -m "$(msg)"
