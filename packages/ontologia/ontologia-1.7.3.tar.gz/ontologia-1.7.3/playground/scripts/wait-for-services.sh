#!/bin/bash
# Wait for all Ontologia Playground services to be healthy
# Usage: ./scripts/wait-for-services.sh [timeout]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TIMEOUT=${1:-300}  # Default timeout: 5 minutes
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-ontologia-playground}

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Service definitions
declare -A SERVICES=(
    ["postgres"]="PostgreSQL Database"
    ["elasticsearch"]="Elasticsearch Search Engine"
    ["redis"]="Redis Cache"
    ["rabbitmq"]="RabbitMQ Message Queue"
    ["temporal"]="Temporal Workflow Engine"
    ["kuzu"]="KùzuDB Graph Database"
    ["dagster-postgres"]="Dagster PostgreSQL"
    ["api"]="Ontologia API"
    ["dagster-webserver"]="Dagster Webserver"
    ["jupyter"]="Jupyter Lab"
    ["dashboard"]="Streamlit Dashboard"
    ["prometheus"]="Prometheus Metrics"
    ["grafana"]="Grafana Visualization"
)

# Health check functions
check_postgres() {
    docker exec ${COMPOSE_PROJECT_NAME}-postgres pg_isready -U ontologia >/dev/null 2>&1
}

check_elasticsearch() {
    curl -f http://localhost:9200/_cluster/health >/dev/null 2>&1
}

check_redis() {
    docker exec ${COMPOSE_PROJECT_NAME}-redis redis-cli --raw incr ping >/dev/null 2>&1
}

check_rabbitmq() {
    docker exec ${COMPOSE_PROJECT_NAME}-rabbitmq rabbitmq-diagnostics ping >/dev/null 2>&1
}

check_temporal() {
    curl -f http://localhost:7233/api/v1/namespaces/default >/dev/null 2>&1
}

check_kuzu() {
    # KùzuDB doesn't have a standard health check, so we check if the container is running
    docker ps --filter "name=${COMPOSE_PROJECT_NAME}-kuzu" --filter "status=running" | grep -q kuzu
}

check_dagster_postgres() {
    docker exec ${COMPOSE_PROJECT_NAME}-dagster-postgres pg_isready -U dagster >/dev/null 2>&1
}

check_api() {
    curl -f http://localhost:8000/health >/dev/null 2>&1
}

check_dagster_webserver() {
    curl -f http://localhost:3000 >/dev/null 2>&1
}

check_jupyter() {
    curl -f http://localhost:8888/api >/dev/null 2>&1
}

check_dashboard() {
    curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1
}

check_prometheus() {
    curl -f http://localhost:9090/-/healthy >/dev/null 2>&1
}

check_grafana() {
    curl -f http://localhost:3001/api/health >/dev/null 2>&1
}

# Wait for a single service
wait_for_service() {
    local service=$1
    local service_name=${SERVICES[$service]}
    local start_time=$(date +%s)

    log_info "Waiting for ${service_name}..."

    while true; do
        if check_${service}; then
            log_success "${service_name} is ready!"
            return 0
        fi

        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if (( elapsed >= TIMEOUT )); then
            log_error "${service_name} failed to start within ${TIMEOUT} seconds"
            return 1
        fi

        echo -n "."
        sleep 2
    done
}

# Check if Docker Compose is running
check_docker_compose() {
    log_info "Checking if Docker Compose is running..."

    if ! docker-compose ps | grep -q "Up"; then
        log_error "Docker Compose services are not running"
        log_info "Please start services with: docker-compose up -d"
        exit 1
    fi

    log_success "Docker Compose services are running"
}

# Show service status
show_status() {
    log_info "Current service status:"
    echo

    for service in "${!SERVICES[@]}"; do
        service_name=${SERVICES[$service]}

        if check_${service} 2>/dev/null; then
            echo -e "  ${GREEN}✅${NC} ${service_name}"
        else
            echo -e "  ${RED}❌${NC} ${service_name}"
        fi
    done
    echo
}

# Main function
main() {
    log_info "🚀 Waiting for Ontologia Playground services..."
    log_info "Timeout: ${TIMEOUT} seconds"
    echo

    # Check if Docker Compose is running
    check_docker_compose

    # Show initial status
    show_status

    # Wait for core services first (in order of dependency)
    log_info "Phase 1: Core Infrastructure Services"
    echo

    core_services=(
        "postgres"
        "elasticsearch"
        "redis"
        "rabbitmq"
        "dagster-postgres"
    )

    for service in "${core_services[@]}"; do
        if ! wait_for_service "$service"; then
            log_error "Core service ${SERVICES[$service]} failed to start"
            exit 1
        fi
    done

    echo
    log_info "Phase 2: Application Services"
    echo

    app_services=(
        "temporal"
        "kuzu"
        "api"
        "dagster-webserver"
    )

    for service in "${app_services[@]}"; do
        if ! wait_for_service "$service"; then
            log_warning "Application service ${SERVICES[$service]} failed to start"
            # Continue with other services
        fi
    done

    echo
    log_info "Phase 3: User Interface Services"
    echo

    ui_services=(
        "jupyter"
        "dashboard"
        "prometheus"
        "grafana"
    )

    for service in "${ui_services[@]}"; do
        if ! wait_for_service "$service"; then
            log_warning "UI service ${SERVICES[$service]} failed to start"
            # Continue with other services
        fi
    done

    # Final status
    echo
    log_success "🎉 All critical services are ready!"
    echo

    show_status

    echo
    log_info "🌐 Access your services:"
    echo "  📊 API Documentation: http://localhost:8000/docs"
    echo "  📓 Jupyter Lab:      http://localhost:8888 (token: jupyter-playground)"
    echo "  🎛️ Temporal UI:       http://localhost:7233"
    echo "  ⚙️  Dagster UI:        http://localhost:3000"
    echo "  🔍 Kibana:            http://localhost:5601"
    echo "  📈 Grafana:           http://localhost:3001 (admin/admin)"
    echo "  🎯 Streamlit:         http://localhost:8501"
    echo "  🗄️  Redis Commander:  http://localhost:8081"
    echo "  📊 Prometheus:        http://localhost:9090"
    echo "  🐘 pgAdmin:           http://localhost:5050"
    echo
    log_info "💡 Tips:"
    echo "  • View logs: docker-compose logs -f [service-name]"
    echo "  • Check status: docker-compose ps"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart service: docker-compose restart [service-name]"
    echo
    log_success "Happy coding with Ontologia! 🚀"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [timeout]"
        echo "Wait for all Ontologia Playground services to be healthy"
        echo ""
        echo "Arguments:"
        echo "  timeout    Timeout in seconds (default: 300)"
        echo ""
        echo "Examples:"
        echo "  $0           # Wait with default timeout"
        echo "  $0 600       # Wait for 10 minutes"
        exit 0
        ;;
    --status)
        show_status
        exit 0
        ;;
esac

# Run main function
main "$@"
