# 🚀 ArgoCD Deployment Guide - Agro Shop

Bu qo'llanma Agro Shop ilovasini ArgoCD orqali GitOps yondashuvi bilan deploy qilish uchun.

## 📋 Prerequisites

### 1. ArgoCD o'rnatish
```bash
# ArgoCD namespace yaratish
kubectl create namespace argocd

# ArgoCD o'rnatish
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# ArgoCD CLI o'rnatish (optional)
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
```

### 2. ArgoCD UI'ga kirish
```bash
# Admin parolni olish
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Browser'da ochish: https://localhost:8080
# Username: admin
# Password: yuqoridagi command'dan olingan parol
```

## 🎯 Deployment Options

### Option 1: Single Application (Recommended for beginners)
```bash
# Bitta application deploy qilish
kubectl apply -f argocd/application.yaml
```

### Option 2: Multi-Environment with ApplicationSet
```bash
# AppProject yaratish
kubectl apply -f argocd/appproject.yaml

# ApplicationSet bilan barcha environmentlar
kubectl apply -f argocd/applicationset.yaml
```

### Option 3: Separate Monitoring Stack
```bash
# Monitoring stack alohida deploy qilish
kubectl apply -f argocd/application-monitoring.yaml

# Application deploy qilish
kubectl apply -f argocd/application.yaml
```

## 🔧 Configuration

### 1. Repository Access
ArgoCD'ga GitHub repository'ga kirish huquqi berish:

```bash
# ArgoCD CLI orqali
argocd repo add https://github.com/Khuma77/DevOPS.git --type git --name agro-shop-repo

# Yoki UI orqali:
# Settings → Repositories → Connect Repo
# Repository URL: https://github.com/Khuma77/DevOPS.git
# Type: git
```

### 2. Image Tag yangilash
GitHub Actions orqali avtomatik yangilanish uchun:

```yaml
# .github/workflows/ci-no-dockerhub.yml da qo'shilgan:
- name: Update ArgoCD Application
  run: |
    # ArgoCD application image tag'ini yangilash
    argocd app set agro-shop --parameter app.image.tag=prod-${{ github.sha }}
    argocd app sync agro-shop
```

### 3. Environment-specific deployment
```bash
# Development
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: agro-shop-dev
  namespace: argocd
spec:
  source:
    helm:
      valueFiles:
        - values.yaml
        - values-dev.yaml
EOF

# Staging
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: agro-shop-staging
  namespace: argocd
spec:
  source:
    helm:
      valueFiles:
        - values.yaml
        - values-staging.yaml
EOF
```

## 📊 Monitoring

### 1. Application Health
```bash
# ArgoCD UI'da application holatini ko'rish
# yoki CLI orqali:
argocd app get agro-shop
argocd app sync agro-shop
```

### 2. Kubernetes Resources
```bash
# Pod'larni ko'rish
kubectl get pods -n agro-shop

# Service'larni ko'rish
kubectl get svc -n agro-shop

# Ingress'ni ko'rish
kubectl get ingress -n agro-shop
```

### 3. Logs
```bash
# Application logs
kubectl logs -l app=agro-shop -n agro-shop

# ArgoCD logs
kubectl logs -l app.kubernetes.io/name=argocd-server -n argocd
```

## 🔄 GitOps Workflow

### 1. Code Push → Auto Deploy
```bash
# 1. Code o'zgartiriladi va GitHub'ga push qilinadi
git add .
git commit -m "feat: new feature"
git push origin main

# 2. GitHub Actions ishga tushadi:
#    - Docker image build qilinadi
#    - GitHub Container Registry'ga push qilinadi
#    - ArgoCD application yangilanadi (optional)

# 3. ArgoCD avtomatik sync qiladi (agar automated sync yoqilgan bo'lsa)
```

### 2. Manual Sync
```bash
# ArgoCD CLI orqali
argocd app sync agro-shop

# ArgoCD UI orqali
# Applications → agro-shop → SYNC
```

### 3. Rollback
```bash
# Oldingi versiyaga qaytish
argocd app rollback agro-shop

# Yoki specific revision'ga
argocd app rollback agro-shop --revision=123
```

## 🛠️ Troubleshooting

### 1. Application Sync Issues
```bash
# Application holatini tekshirish
argocd app get agro-shop

# Sync qilishga majburlash
argocd app sync agro-shop --force

# Prune qilish (keraksiz resource'larni o'chirish)
argocd app sync agro-shop --prune
```

### 2. Image Pull Issues
```bash
# Image pull secret yaratish (agar private registry bo'lsa)
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=your-username \
  --docker-password=your-token \
  --namespace=agro-shop

# values.yaml'da qo'shish:
global:
  imagePullSecrets:
    - name: ghcr-secret
```

### 3. Ingress Issues
```bash
# Ingress controller o'rnatish
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# DNS sozlash (local development uchun)
echo "127.0.0.1 agro-shop.local" | sudo tee -a /etc/hosts
```

## 📈 Scaling

### 1. Manual Scaling
```bash
# Replica count o'zgartirish
argocd app set agro-shop --parameter app.replicaCount=5
argocd app sync agro-shop
```

### 2. Auto Scaling (HPA)
```yaml
# values.yaml'da:
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### 3. Resource Limits
```yaml
# values.yaml'da:
app:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

## 🔐 Security

### 1. RBAC
```bash
# AppProject bilan role-based access
kubectl apply -f argocd/appproject.yaml
```

### 2. Network Policies
```yaml
# values.yaml'da:
networkPolicy:
  enabled: true
```

### 3. Pod Security
```yaml
# values.yaml'da:
app:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
```

## 🎉 Success!

Agar hammasi to'g'ri sozlangan bo'lsa:

1. **ArgoCD UI**: https://localhost:8080
2. **Application**: http://agro-shop.local
3. **Grafana**: http://grafana.agro-shop.local
4. **Prometheus**: http://prometheus.agro-shop.local

GitOps workflow tayyor! Har bir code push avtomatik ravishda production'ga deploy bo'ladi! 🚀