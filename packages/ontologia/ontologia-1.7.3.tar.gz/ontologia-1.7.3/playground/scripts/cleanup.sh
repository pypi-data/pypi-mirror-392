#!/bin/bash
# Cleanup Ontologia Playground
# Usage: ./scripts/cleanup.sh [options]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
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

# Show help
show_help() {
    echo "Ontologia Playground Cleanup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all          Remove everything (containers, volumes, networks, data)"
    echo "  --containers   Remove only containers"
    echo "  --volumes      Remove only volumes"
    echo "  --networks     Remove only networks"
    echo "  --data         Remove only data directories"
    echo "  --images       Remove Ontologia images"
    echo "  --dry-run      Show what would be removed without actually removing"
    echo "  --help, -h     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all              # Complete cleanup"
    echo "  $0 --containers       # Remove containers only"
    echo "  $0 --volumes          # Remove volumes only"
    echo "  $0 --dry-run          # Preview what would be removed"
}

# Check if Docker is running
check_docker() {
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi
}

# Stop and remove containers
cleanup_containers() {
    log_info "Stopping and removing containers..."

    # Stop containers
    if docker-compose ps | grep -q "Up"; then
        log_info "Stopping containers..."
        docker-compose down
        log_success "Containers stopped"
    else
        log_info "No containers are running"
    fi

    # Remove stopped containers
    local containers=$(docker ps -a --filter "name=${COMPOSE_PROJECT_NAME}" --format "{{.Names}}" 2>/dev/null || true)
    if [[ -n "$containers" ]]; then
        log_info "Removing stopped containers..."
        echo "$containers" | xargs -r docker rm -f
        log_success "Containers removed"
    else
        log_info "No containers to remove"
    fi
}

# Remove volumes
cleanup_volumes() {
    log_info "Removing volumes..."

    # Remove Docker volumes
    local volumes=$(docker volume ls --filter "name=${COMPOSE_PROJECT_NAME}" --format "{{.Name}}" 2>/dev/null || true)
    if [[ -n "$volumes" ]]; then
        log_warning "This will delete all data in the following volumes:"
        echo "$volumes" | sed 's/^/  - /'

        if [[ "${DRY_RUN:-}" != "true" ]]; then
            echo "$volumes" | xargs -r docker volume rm -f
            log_success "Volumes removed"
        else
            log_info "[DRY RUN] Would remove volumes: $volumes"
        fi
    else
        log_info "No volumes to remove"
    fi
}

# Remove networks
cleanup_networks() {
    log_info "Removing networks..."

    local networks=$(docker network ls --filter "name=${COMPOSE_PROJECT_NAME}" --format "{{.Name}}" 2>/dev/null || true)
    if [[ -n "$networks" ]]; then
        log_info "Removing networks..."
        echo "$networks" | xargs -r docker network rm
        log_success "Networks removed"
    else
        log_info "No networks to remove"
    fi
}

# Remove data directories
cleanup_data() {
    log_info "Removing data directories..."

    local data_dirs=(
        "data"
        "logs"
        "monitoring/grafana/data"
        "monitoring/prometheus/data"
    )

    for dir in "${data_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            if [[ "${DRY_RUN:-}" != "true" ]]; then
                log_info "Removing directory: $dir"
                rm -rf "$dir"
                log_success "Removed $dir"
            else
                log_info "[DRY RUN] Would remove directory: $dir"
            fi
        else
            log_info "Directory does not exist: $dir"
        fi
    done
}

# Remove Ontologia images
cleanup_images() {
    log_info "Removing Ontologia images..."

    local images=$(docker images --filter "reference=ontologia*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
    if [[ -n "$images" ]]; then
        log_warning "This will remove the following images:"
        echo "$images" | sed 's/^/  - /'

        if [[ "${DRY_RUN:-}" != "true" ]]; then
            echo "$images" | xargs -r docker rmi -f
            log_success "Images removed"
        else
            log_info "[DRY RUN] Would remove images: $images"
        fi
    else
        log_info "No Ontologia images to remove"
    fi
}

# Show current status
show_status() {
    log_info "Current Ontologia Playground status:"
    echo

    # Containers
    local containers=$(docker ps -a --filter "name=${COMPOSE_PROJECT_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true)
    if [[ -n "$containers" ]]; then
        echo "📦 Containers:"
        echo "$containers"
        echo
    else
        echo "📦 No containers found"
        echo
    fi

    # Volumes
    local volumes=$(docker volume ls --filter "name=${COMPOSE_PROJECT_NAME}" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null || true)
    if [[ -n "$volumes" ]]; then
        echo "💾 Volumes:"
        echo "$volumes"
        echo
    else
        echo "💾 No volumes found"
        echo
    fi

    # Networks
    local networks=$(docker network ls --filter "name=${COMPOSE_PROJECT_NAME}" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null || true)
    if [[ -n "$networks" ]]; then
        echo "🌐 Networks:"
        echo "$networks"
        echo
    else
        echo "🌐 No networks found"
        echo
    fi

    # Data directories
    echo "📁 Data directories:"
    local data_dirs=("data" "logs" "monitoring/grafana/data" "monitoring/prometheus/data")
    for dir in "${data_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            local size=$(du -sh "$dir" 2>/dev/null | cut -f1 || echo "unknown")
            echo "  ✅ $dir ($size)"
        else
            echo "  ❌ $dir (not found)"
        fi
    done
    echo
}

# Complete cleanup
cleanup_all() {
    log_warning "🚨 COMPLETE CLEANUP - This will remove ALL data!"
    echo

    if [[ "${DRY_RUN:-}" != "true" ]]; then
        read -p "Are you sure you want to remove everything? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_info "Cleanup cancelled"
            exit 0
        fi
    fi

    cleanup_containers
    cleanup_volumes
    cleanup_networks
    cleanup_data
    cleanup_images

    if [[ "${DRY_RUN:-}" != "true" ]]; then
        log_success "🎉 Complete cleanup finished!"
    else
        log_info "[DRY RUN] Complete cleanup preview finished"
    fi
}

# Main function
main() {
    local action=${1:---help}

    case "$action" in
        --all)
            check_docker
            cleanup_all
            ;;
        --containers)
            check_docker
            cleanup_containers
            ;;
        --volumes)
            check_docker
            cleanup_volumes
            ;;
        --networks)
            check_docker
            cleanup_networks
            ;;
        --data)
            cleanup_data
            ;;
        --images)
            check_docker
            cleanup_images
            ;;
        --status)
            check_docker
            show_status
            ;;
        --dry-run)
            DRY_RUN=true
            log_info "DRY RUN MODE - Showing what would be removed"
            echo
            check_docker
            cleanup_all
            ;;
        --help|-h)
            show_help
            ;;
        *)
            log_error "Unknown option: $action"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
