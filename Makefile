.PHONY: migrate-apply
migrate-apply: ## apply alembic migrations to database/schema
	alembic upgrade head

.PHONY: migrate-create
migrate-create:  ## Create new alembic database migration aka database revision.
	alembic revision --autogenerate -m "$(msg)"

.PHONY: deploy-backend-build-push
deploy-backend-build:
	docker buildx build --platform linux/amd64 -t saidmagomedov/backend-app:latest -f Dockerfile . --push

.PHONY: deploy-worker-build-push
deploy-worker-build:
	docker buildx build --platform linux/amd64 -t saidmagomedov/backend-worker:latest -f Worker.Dockerfile . --push


.PHONY: deploy-worker-enhance-build-push
deploy-worker-build:
	docker buildx build --platform linux/amd64 -t saidmagomedov/backend-worker-enhace:latest -f WorkerEnhance.Dockerfile . --push
