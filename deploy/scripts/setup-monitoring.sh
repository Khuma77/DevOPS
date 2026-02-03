#!/bin/bash

# 🚀 Agro Shop - Complete Monitoring Stack Setup
# This script sets up the complete monitoring infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE_MONITORING="monitoring"
NAMESPACE_APP="agro-shop"
HELM_RELEASE_MONITORING="agro-monitoring"
HELM_RELEASE_APP="agro-shop"

echo -e "${BLUE}🚀 Starting Agro Shop Monitoring Stack Setup${NC}"

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

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    print_error "helm is not installed"
    exit 1
fi

print_status "Prerequisites check passed"

# Create namespaces
echo -e "${BLUE}📦 Creating namespaces...${NC}"
kubectl create namespace $NAMESPACE_MONITORING --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace $NAMESPACE_APP --dry-run=client -o yaml | kubectl apply -f -
print_status "Namespaces created"

# Add Helm repositories
echo -e "${BLUE}📚 Adding Helm repositories...${NC}"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add loki https://grafana.github.io/loki/charts
helm repo update
print_status "Helm repositories added"

# Install Prometheus
echo -e "${BLUE}📊 Installing Prometheus...${NC}"
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace $NAMESPACE_MONITORING \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=10Gi \
  --set grafana.adminPassword=admin123 \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.size=5Gi \
  --wait --timeout=10m

print_status "Prometheus installed"

# Install Loki
echo -e "${BLUE}📝 Installing Loki...${NC}"
helm upgrade --install loki loki/loki-stack \
  --namespace $NAMESPACE_MONITORING \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=5Gi \
  --set promtail.enabled=true \
  --wait --timeout=5m

print_status "Loki installed"

# Create custom Grafana dashboards ConfigMap
echo -e "${BLUE}📈 Creating custom Grafana dashboards...${NC}"
kubectl create configmap agro-shop-dashboards \
  --from-file=monitoring/grafana/dashboards/ \
  --namespace=$NAMESPACE_MONITORING \
  --dry-run=client -o yaml | kubectl apply -f -

# Label the ConfigMap for Grafana to pick it up
kubectl label configmap agro-shop-dashboards \
  grafana_dashboard=1 \
  --namespace=$NAMESPACE_MONITORING \
  --overwrite

print_status "Custom dashboards created"

# Install the application
echo -e "${BLUE}🌾 Installing Agro Shop application...${NC}"
helm upgrade --install $HELM_RELEASE_APP ./helm/agro-shop \
  --namespace $NAMESPACE_APP \
  --set monitoring.enabled=true \
  --set serviceMonitor.enabled=true \
  --set app.image.tag=prod-latest \
  --wait --timeout=5m

print_status "Application installed"

# Wait for pods to be ready
echo -e "${BLUE}⏳ Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n $NAMESPACE_MONITORING --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n $NAMESPACE_MONITORING --timeout=300s
kubectl wait --for=condition=ready pod -l app=agro-shop -n $NAMESPACE_APP --timeout=300s

print_status "All pods are ready"

# Create port-forward scripts
echo -e "${BLUE}🔗 Creating port-forward scripts...${NC}"

cat > deploy/scripts/port-forward-monitoring.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting port-forwards for monitoring stack..."
echo "📊 Grafana will be available at: http://localhost:3000 (admin/admin123)"
echo "📈 Prometheus will be available at: http://localhost:9090"
echo "📝 Loki will be available at: http://localhost:3100"
echo "🌾 Agro Shop will be available at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all port-forwards"

# Start port-forwards in background
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
kubectl port-forward -n monitoring svc/loki 3100:3100 &
kubectl port-forward -n agro-shop svc/agro-shop 8080:80 &

# Wait for all background processes
wait
EOF

chmod +x deploy/scripts/port-forward-monitoring.sh

cat > deploy/scripts/stop-port-forwards.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping all port-forwards..."
pkill -f "kubectl port-forward" || true
echo "✅ All port-forwards stopped"
EOF

chmod +x deploy/scripts/stop-port-forwards.sh

print_status "Port-forward scripts created"

# Display access information
echo -e "${BLUE}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${GREEN}📊 Access URLs (after running port-forward script):${NC}"
echo -e "  • Grafana Dashboard: ${BLUE}http://localhost:3000${NC} (admin/admin123)"
echo -e "  • Prometheus: ${BLUE}http://localhost:9090${NC}"
echo -e "  • Loki: ${BLUE}http://localhost:3100${NC}"
echo -e "  • Agro Shop App: ${BLUE}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}🔧 Management Commands:${NC}"
echo -e "  • Start port-forwards: ${YELLOW}./deploy/scripts/port-forward-monitoring.sh${NC}"
echo -e "  • Stop port-forwards: ${YELLOW}./deploy/scripts/stop-port-forwards.sh${NC}"
echo ""
echo -e "${GREEN}📈 Monitoring Features:${NC}"
echo -e "  • ✅ Prometheus metrics collection"
echo -e "  • ✅ Grafana dashboards with custom business metrics"
echo -e "  • ✅ Loki log aggregation"
echo -e "  • ✅ Application performance monitoring"
echo -e "  • ✅ Infrastructure monitoring"
echo ""
echo -e "${GREEN}🚀 Next Steps:${NC}"
echo -e "  1. Run: ${YELLOW}./deploy/scripts/port-forward-monitoring.sh${NC}"
echo -e "  2. Open Grafana at http://localhost:3000"
echo -e "  3. Import custom dashboards from monitoring/grafana/dashboards/"
echo -e "  4. Configure alerts in Grafana"
echo ""
echo -e "${BLUE}Happy monitoring! 🎯${NC}"