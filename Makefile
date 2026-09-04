.PHONY: up down verify
up:
	docker compose up --build
down:
	docker compose down
verify:
	powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
