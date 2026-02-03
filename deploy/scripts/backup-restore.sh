#!/bin/bash

# 💾 Agro Shop - Backup and Disaster Recovery Script
# This script handles backup and restore operations for the Agro Shop application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
APP_NAME="agro-shop"
NAMESPACE="agro-shop"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Help function
show_help() {
    echo -e "${BLUE}💾 Agro Shop Backup & Restore Tool${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  backup-local     Create backup of local deployment"
    echo "  backup-k8s       Create backup of Kubernetes deployment"
    echo "  restore-local    Restore from local backup"
    echo "  restore-k8s      Restore to Kubernetes deployment"
    echo "  list-backups     List available backups"
    echo "  cleanup-old      Remove old backups (keep last 5)"
    echo ""
    echo "Options:"
    echo "  --backup-file    Specify backup file for restore operations"
    echo "  --namespace      Kubernetes namespace (default: agro-shop)"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup-local"
    echo "  $0 restore-local --backup-file backups/backup_20240127_143022.tar.gz"
    echo "  $0 backup-k8s --namespace agro-shop-prod"
}

# Create backup directory
create_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    print_status "Backup directory created: $BACKUP_DIR"
}

# Backup local deployment
backup_local() {
    print_info "Starting local deployment backup..."
    create_backup_dir
    
    local backup_name="backup_local_${TIMESTAMP}"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    # Create temporary backup directory
    mkdir -p "$backup_path"
    
    # Backup database
    if [ -f "agro.db" ]; then
        cp agro.db "$backup_path/"
        print_status "Database backed up"
    else
        print_warning "Database file not found"
    fi
    
    # Backup application configuration
    cp -r helm/ "$backup_path/" 2>/dev/null || print_warning "Helm charts not found"
    cp -r argocd/ "$backup_path/" 2>/dev/null || print_warning "ArgoCD configs not found"
    cp -r monitoring/ "$backup_path/" 2>/dev/null || print_warning "Monitoring configs not found"
    
    # Backup Docker configurations
    cp docker-compose*.yml "$backup_path/" 2>/dev/null || print_warning "Docker compose files not found"
    cp Dockerfile* "$backup_path/" 2>/dev/null || print_warning "Dockerfiles not found"
    
    # Backup application code (key files only)
    cp -r api/ "$backup_path/" 2>/dev/null || print_warning "API code not found"
    cp -r admin/ "$backup_path/" 2>/dev/null || print_warning "Admin code not found"
    cp -r models/ "$backup_path/" 2>/dev/null || print_warning "Models not found"
    cp -r templates/ "$backup_path/" 2>/dev/null || print_warning "Templates not found"
    cp -r static/ "$backup_path/" 2>/dev/null || print_warning "Static files not found"
    
    # Backup main application files
    cp app.py "$backup_path/" 2>/dev/null || print_warning "app.py not found"
    cp requirements.txt "$backup_path/" 2>/dev/null || print_warning "requirements.txt not found"
    cp database.py "$backup_path/" 2>/dev/null || print_warning "database.py not found"
    cp logging_config.py "$backup_path/" 2>/dev/null || print_warning "logging_config.py not found"
    
    # Create backup metadata
    cat > "$backup_path/backup_metadata.json" << EOF
{
    "backup_type": "local",
    "timestamp": "$TIMESTAMP",
    "date": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
    "backup_size": "$(du -sh $backup_path | cut -f1)"
}
EOF
    
    # Create compressed archive
    local archive_name="${backup_name}.tar.gz"
    tar -czf "${BACKUP_DIR}/${archive_name}" -C "$BACKUP_DIR" "$backup_name"
    
    # Remove temporary directory
    rm -rf "$backup_path"
    
    print_status "Local backup completed: ${BACKUP_DIR}/${archive_name}"
    
    # Show backup info
    local backup_size=$(du -sh "${BACKUP_DIR}/${archive_name}" | cut -f1)
    print_info "Backup size: $backup_size"
}

# Backup Kubernetes deployment
backup_k8s() {
    print_info "Starting Kubernetes deployment backup..."
    create_backup_dir
    
    local backup_name="backup_k8s_${TIMESTAMP}"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    # Create temporary backup directory
    mkdir -p "$backup_path"
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Backup Kubernetes resources
    print_info "Backing up Kubernetes resources..."
    
    # Backup deployments
    kubectl get deployments -n "$NAMESPACE" -o yaml > "$backup_path/deployments.yaml" 2>/dev/null || print_warning "No deployments found"
    
    # Backup services
    kubectl get services -n "$NAMESPACE" -o yaml > "$backup_path/services.yaml" 2>/dev/null || print_warning "No services found"
    
    # Backup configmaps
    kubectl get configmaps -n "$NAMESPACE" -o yaml > "$backup_path/configmaps.yaml" 2>/dev/null || print_warning "No configmaps found"
    
    # Backup secrets (without sensitive data)
    kubectl get secrets -n "$NAMESPACE" -o yaml | sed 's/data:/data: {}/' > "$backup_path/secrets_structure.yaml" 2>/dev/null || print_warning "No secrets found"
    
    # Backup ingress
    kubectl get ingress -n "$NAMESPACE" -o yaml > "$backup_path/ingress.yaml" 2>/dev/null || print_warning "No ingress found"
    
    # Backup persistent volume claims
    kubectl get pvc -n "$NAMESPACE" -o yaml > "$backup_path/pvc.yaml" 2>/dev/null || print_warning "No PVCs found"
    
    # Backup HPA
    kubectl get hpa -n "$NAMESPACE" -o yaml > "$backup_path/hpa.yaml" 2>/dev/null || print_warning "No HPA found"
    
    # Backup database from pod (if exists)
    local db_pod=$(kubectl get pods -n "$NAMESPACE" -l app="$APP_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ ! -z "$db_pod" ]; then
        print_info "Backing up database from pod: $db_pod"
        kubectl exec -n "$NAMESPACE" "$db_pod" -- sqlite3 /app/data/agro.db .dump > "$backup_path/database_dump.sql" 2>/dev/null || print_warning "Database backup failed"
    fi
    
    # Backup Helm values
    if [ -d "helm/" ]; then
        cp -r helm/ "$backup_path/"
        print_status "Helm charts backed up"
    fi
    
    # Backup ArgoCD configurations
    if [ -d "argocd/" ]; then
        cp -r argocd/ "$backup_path/"
        print_status "ArgoCD configurations backed up"
    fi
    
    # Create backup metadata
    cat > "$backup_path/backup_metadata.json" << EOF
{
    "backup_type": "kubernetes",
    "timestamp": "$TIMESTAMP",
    "date": "$(date -Iseconds)",
    "namespace": "$NAMESPACE",
    "kubernetes_version": "$(kubectl version --short --client 2>/dev/null | grep Client || echo 'unknown')",
    "cluster_info": "$(kubectl cluster-info | head -1 || echo 'unknown')",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')"
}
EOF
    
    # Create compressed archive
    local archive_name="${backup_name}.tar.gz"
    tar -czf "${BACKUP_DIR}/${archive_name}" -C "$BACKUP_DIR" "$backup_name"
    
    # Remove temporary directory
    rm -rf "$backup_path"
    
    print_status "Kubernetes backup completed: ${BACKUP_DIR}/${archive_name}"
    
    # Show backup info
    local backup_size=$(du -sh "${BACKUP_DIR}/${archive_name}" | cut -f1)
    print_info "Backup size: $backup_size"
}

# Restore local deployment
restore_local() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "Backup file not specified. Use --backup-file option."
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_info "Starting local deployment restore from: $backup_file"
    
    # Create temporary restore directory
    local restore_dir="./restore_temp_${TIMESTAMP}"
    mkdir -p "$restore_dir"
    
    # Extract backup
    tar -xzf "$backup_file" -C "$restore_dir"
    
    # Find the backup directory (should be the only directory in restore_dir)
    local backup_content_dir=$(find "$restore_dir" -mindepth 1 -maxdepth 1 -type d | head -1)
    
    if [ -z "$backup_content_dir" ]; then
        print_error "Invalid backup file structure"
        rm -rf "$restore_dir"
        exit 1
    fi
    
    # Show backup metadata
    if [ -f "$backup_content_dir/backup_metadata.json" ]; then
        print_info "Backup metadata:"
        cat "$backup_content_dir/backup_metadata.json" | jq . 2>/dev/null || cat "$backup_content_dir/backup_metadata.json"
    fi
    
    # Confirm restore
    echo -e "${YELLOW}⚠️  This will overwrite existing files. Continue? (y/N)${NC}"
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Restore cancelled"
        rm -rf "$restore_dir"
        exit 0
    fi
    
    # Restore database
    if [ -f "$backup_content_dir/agro.db" ]; then
        cp "$backup_content_dir/agro.db" ./
        print_status "Database restored"
    fi
    
    # Restore configurations
    [ -d "$backup_content_dir/helm" ] && cp -r "$backup_content_dir/helm" ./ && print_status "Helm charts restored"
    [ -d "$backup_content_dir/argocd" ] && cp -r "$backup_content_dir/argocd" ./ && print_status "ArgoCD configs restored"
    [ -d "$backup_content_dir/monitoring" ] && cp -r "$backup_content_dir/monitoring" ./ && print_status "Monitoring configs restored"
    
    # Restore Docker files
    [ -f "$backup_content_dir/docker-compose.yml" ] && cp "$backup_content_dir/docker-compose.yml" ./ && print_status "Docker compose restored"
    [ -f "$backup_content_dir/Dockerfile" ] && cp "$backup_content_dir/Dockerfile" ./ && print_status "Dockerfile restored"
    
    # Restore application code
    [ -d "$backup_content_dir/api" ] && cp -r "$backup_content_dir/api" ./ && print_status "API code restored"
    [ -d "$backup_content_dir/admin" ] && cp -r "$backup_content_dir/admin" ./ && print_status "Admin code restored"
    [ -d "$backup_content_dir/models" ] && cp -r "$backup_content_dir/models" ./ && print_status "Models restored"
    [ -d "$backup_content_dir/templates" ] && cp -r "$backup_content_dir/templates" ./ && print_status "Templates restored"
    [ -d "$backup_content_dir/static" ] && cp -r "$backup_content_dir/static" ./ && print_status "Static files restored"
    
    # Restore main files
    [ -f "$backup_content_dir/app.py" ] && cp "$backup_content_dir/app.py" ./ && print_status "app.py restored"
    [ -f "$backup_content_dir/requirements.txt" ] && cp "$backup_content_dir/requirements.txt" ./ && print_status "requirements.txt restored"
    [ -f "$backup_content_dir/database.py" ] && cp "$backup_content_dir/database.py" ./ && print_status "database.py restored"
    
    # Cleanup
    rm -rf "$restore_dir"
    
    print_status "Local deployment restore completed successfully!"
    print_info "You may need to restart the application and reinstall dependencies"
}

# Restore Kubernetes deployment
restore_k8s() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "Backup file not specified. Use --backup-file option."
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_info "Starting Kubernetes deployment restore from: $backup_file"
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Create temporary restore directory
    local restore_dir="./restore_temp_${TIMESTAMP}"
    mkdir -p "$restore_dir"
    
    # Extract backup
    tar -xzf "$backup_file" -C "$restore_dir"
    
    # Find the backup directory
    local backup_content_dir=$(find "$restore_dir" -mindepth 1 -maxdepth 1 -type d | head -1)
    
    if [ -z "$backup_content_dir" ]; then
        print_error "Invalid backup file structure"
        rm -rf "$restore_dir"
        exit 1
    fi
    
    # Show backup metadata
    if [ -f "$backup_content_dir/backup_metadata.json" ]; then
        print_info "Backup metadata:"
        cat "$backup_content_dir/backup_metadata.json" | jq . 2>/dev/null || cat "$backup_content_dir/backup_metadata.json"
    fi
    
    # Confirm restore
    echo -e "${YELLOW}⚠️  This will overwrite existing Kubernetes resources in namespace '$NAMESPACE'. Continue? (y/N)${NC}"
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Restore cancelled"
        rm -rf "$restore_dir"
        exit 0
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Restore Kubernetes resources
    print_info "Restoring Kubernetes resources..."
    
    [ -f "$backup_content_dir/deployments.yaml" ] && kubectl apply -f "$backup_content_dir/deployments.yaml" -n "$NAMESPACE" && print_status "Deployments restored"
    [ -f "$backup_content_dir/services.yaml" ] && kubectl apply -f "$backup_content_dir/services.yaml" -n "$NAMESPACE" && print_status "Services restored"
    [ -f "$backup_content_dir/configmaps.yaml" ] && kubectl apply -f "$backup_content_dir/configmaps.yaml" -n "$NAMESPACE" && print_status "ConfigMaps restored"
    [ -f "$backup_content_dir/ingress.yaml" ] && kubectl apply -f "$backup_content_dir/ingress.yaml" -n "$NAMESPACE" && print_status "Ingress restored"
    [ -f "$backup_content_dir/pvc.yaml" ] && kubectl apply -f "$backup_content_dir/pvc.yaml" -n "$NAMESPACE" && print_status "PVCs restored"
    [ -f "$backup_content_dir/hpa.yaml" ] && kubectl apply -f "$backup_content_dir/hpa.yaml" -n "$NAMESPACE" && print_status "HPA restored"
    
    # Wait for pods to be ready
    print_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app="$APP_NAME" -n "$NAMESPACE" --timeout=300s || print_warning "Some pods may not be ready yet"
    
    # Restore database if dump exists
    if [ -f "$backup_content_dir/database_dump.sql" ]; then
        print_info "Restoring database..."
        local db_pod=$(kubectl get pods -n "$NAMESPACE" -l app="$APP_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
        if [ ! -z "$db_pod" ]; then
            kubectl exec -n "$NAMESPACE" "$db_pod" -- sqlite3 /app/data/agro.db < "$backup_content_dir/database_dump.sql" && print_status "Database restored"
        else
            print_warning "No application pod found for database restore"
        fi
    fi
    
    # Cleanup
    rm -rf "$restore_dir"
    
    print_status "Kubernetes deployment restore completed successfully!"
    print_info "Check pod status with: kubectl get pods -n $NAMESPACE"
}

# List available backups
list_backups() {
    print_info "Available backups in $BACKUP_DIR:"
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        print_warning "No backups found"
        return
    fi
    
    echo ""
    printf "%-30s %-15s %-10s %-20s\n" "BACKUP FILE" "TYPE" "SIZE" "DATE"
    echo "$(printf '%.0s-' {1..80})"
    
    for backup in "$BACKUP_DIR"/*.tar.gz; do
        if [ -f "$backup" ]; then
            local filename=$(basename "$backup")
            local size=$(du -sh "$backup" | cut -f1)
            local date=$(stat -c %y "$backup" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
            local type="unknown"
            
            if [[ "$filename" == *"local"* ]]; then
                type="local"
            elif [[ "$filename" == *"k8s"* ]]; then
                type="kubernetes"
            fi
            
            printf "%-30s %-15s %-10s %-20s\n" "$filename" "$type" "$size" "$date"
        fi
    done
}

# Cleanup old backups
cleanup_old() {
    local keep_count=5
    
    print_info "Cleaning up old backups (keeping last $keep_count)..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_warning "Backup directory does not exist"
        return
    fi
    
    local backup_count=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    
    if [ "$backup_count" -le "$keep_count" ]; then
        print_info "No cleanup needed. Found $backup_count backups (keeping $keep_count)"
        return
    fi
    
    # Remove old backups
    ls -1t "$BACKUP_DIR"/*.tar.gz | tail -n +$((keep_count + 1)) | while read -r old_backup; do
        rm -f "$old_backup"
        print_status "Removed old backup: $(basename "$old_backup")"
    done
    
    print_status "Cleanup completed. Kept $keep_count most recent backups"
}

# Main script logic
main() {
    local command="$1"
    shift
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup-file)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    case "$command" in
        backup-local)
            backup_local
            ;;
        backup-k8s)
            backup_k8s
            ;;
        restore-local)
            restore_local "$BACKUP_FILE"
            ;;
        restore-k8s)
            restore_k8s "$BACKUP_FILE"
            ;;
        list-backups)
            list_backups
            ;;
        cleanup-old)
            cleanup_old
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"