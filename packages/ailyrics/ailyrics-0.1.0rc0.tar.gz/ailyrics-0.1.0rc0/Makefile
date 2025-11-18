# Lyrics Server Makefile
# Simplify container operations and testing workflow

.PHONY: help docker-build docker-up docker-down docker-test docker-api docker-logs docker-shell docker-clean fmt check

# Default target
help:
	@echo "🎵 Lyrics Server - Container Operations Help"
	@echo "=============================="
	@echo ""
	@echo "📦 Container Management:"
	@echo "  make docker-build  - Build container image"
	@echo "  make docker-up     - Start container services"
	@echo "  make docker-down   - Stop container services"
	@echo "  make docker-logs   - View container logs"
	@echo "  make docker-shell  - Enter container shell"
	@echo "  make docker-clean  - Clean containers and images"
	@echo ""
	@echo "🧪 Testing and Validation:"
	@echo "  make docker-test   - Build, start and run complete tests"
	@echo "  make docker-api    - Start container API service only"
	@echo "  make test-health   - Quick health check"
	@echo "  make test-bash     - Test bash command execution"
	@echo "  make test-skills   - Test skills system"
	@echo ""
	@echo "🔧 Development and Debugging:"
	@echo "  make dev-local     - Start local development server"
	@echo "  make test      - Run local tests"
	@echo ""
	@echo "🎯 Code Quality Checks:"
	@echo "  make fmt        	- Format all code"
	@echo "  make check         - Run all code checks (ruff-check)"
	@echo ""

# Container build
docker-build:
	@echo "📦 Building container image..."
	@docker compose -f docker-compose.test.yml build

# Start container services
docker-up:
	@echo "🚀 Starting container services..."
	@docker compose -f docker-compose.test.yml --profile testing up -d
	@echo "⏳ Waiting for services to start..."
	@sleep 3
	@echo "✅ Container services started"

# Stop container services
docker-down:
	@echo "🛑 Stopping container services..."
	@docker compose -f docker-compose.test.yml down
	@echo "✅ Container services stopped"

# View container logs
docker-logs:
	@echo "📋 Viewing container logs..."
	@docker compose -f docker-compose.test.yml logs --tail=50 -f

# Enter container shell
docker-shell:
	@echo "🐚 Entering container shell..."
	@docker exec -it lyrics-lyrics-test-1 /bin/bash

# Complete container testing workflow
docker-test: docker-build docker-up
	@echo "🧪 Running complete API tests..."
	@echo "⏳ Waiting for services to fully start..."
	@sleep 3
	@echo "🏃 Testing all API_SPEC.md and DESIGN.md requirements..."
	@uv run pytest tests/integration

# Start API service only
docker-api: docker-build docker-up
	@echo "🌐 Container API service started"
	@echo "📍 Access URL: http://localhost:8870"
	@echo "🔍 Health check: curl http://localhost:8870/api/v1/health"

# Quick health check
test-health:
	@echo "🏥 Performing health check..."
	@curl -s http://localhost:8870/api/v1/health | jq . || echo "❌ Health check failed"

# Test bash command
test-bash:
	@echo "🖥️  Testing bash command execution..."
	@curl -s -X POST http://localhost:8870/api/v1/bash/execute \
		-H "Content-Type: application/json" \
		-d '{"command":"pwd"}' | jq . || echo "❌ Bash command test failed"

# Test skills system
test-skills:
	@echo "📚 Testing skills system..."
	@curl -s http://localhost:8870/api/v1/skills | jq . || echo "❌ Skills system test failed"

# Local development server
dev-local:
	@echo "🔧 Starting local development server..."
	@uv run python -m lyrics.server --host 0.0.0.0 --port 8081

# Local testing
test:
	@echo "🧪 Running local tests..."
	@uv run pytest tests/unit

# Clean containers and images
docker-clean:
	@echo "🧹 Cleaning containers and images..."
	@docker compose -f docker-compose.test.yml down --rmi all --volumes
	@echo "✅ Cleanup completed"

# Quick restart
docker-restart: docker-down docker-up
	@echo "🔄 Container restarted"

# Check container status
docker-status:
	@echo "📊 Container status:"
	@docker compose -f docker-compose.test.yml ps
	@echo ""
	@echo "🌐 Port mapping:"
	@docker port lyrics-lyrics-test-1 2>/dev/null || echo "Container not running"

# Quick debug workflow
debug: docker-down docker-build docker-up
	@echo "🔍 Starting debug mode..."
	@sleep 3
	@echo "📋 Container logs:"
	@docker compose -f docker-compose.test.yml logs --tail=20
	@echo ""
	@echo "🏥 Quick health check:"
	@$(MAKE) test-health

# Ruff code check
check:
	@echo "🔍 Running ruff code checks..."
	@uv run ruff format --check src/ tests/
	@uv run ruff check --select E,F,I src/ tests/

fmt:
	@echo "🔧 Auto-fixing issues found by ruff..."
	@uv run ruff format src/ tests/
	@uv run ruff check --select E,F,I --fix src/ tests/
