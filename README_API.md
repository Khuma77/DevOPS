# Agro Shop API va Monitoring

Bu loyiha uchun to'liq REST API va monitoring tizimi qo'shildi.

## 🚀 Ishga tushirish

### 1. Dependencies o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Ilovani ishga tushirish
```bash
python app.py
```

### 3. Docker bilan ishga tushirish (Monitoring bilan)
```bash
docker-compose up -d
```

## 📡 API Endpoints

### Products API
- `GET /api/v1/products` - Barcha mahsulotlar
- `GET /api/v1/products/{id}` - Bitta mahsulot
- `POST /api/v1/products` - Yangi mahsulot yaratish
- `PUT /api/v1/products/{id}` - Mahsulotni yangilash
- `DELETE /api/v1/products/{id}` - Mahsulotni o'chirish

### Orders API
- `GET /api/v1/orders` - Barcha buyurtmalar
- `GET /api/v1/orders/{id}` - Bitta buyurtma
- `POST /api/v1/orders` - Yangi buyurtma yaratish

### Statistics API
- `GET /api/v1/stats` - Ilovaning statistikasi

### Monitoring Endpoints
- `GET /metrics` - Prometheus metrics
- `GET /health` - Health check

## 📊 Monitoring Stack

### Prometheus (Port 9090)
- Metrics yig'ish va saqlash
- URL: http://localhost:9090

### Grafana (Port 3000)
- Vizualizatsiya va dashboard
- URL: http://localhost:3000
- Login: admin / admin123

### Loki (Port 3100)
- Log aggregation
- URL: http://localhost:3100

## 📈 Metrics

Quyidagi metrikalar yig'iladi:

### Application Metrics
- `api_requests_total` - API so'rovlar soni
- `api_request_duration_seconds` - API javob vaqti
- `active_orders_total` - Faol buyurtmalar soni
- `products_count_total` - Mahsulotlar soni

### System Metrics
- `system_cpu_usage_percent` - CPU foydalanish foizi
- `system_memory_usage_percent` - Xotira foydalanish foizi
- `system_disk_usage_percent` - Disk foydalanish foizi

## 🧪 API Test

API ni test qilish uchun:

```bash
python api_test.py
```

## 📝 Log Format

Barcha loglar JSON formatida yoziladi:

```json
{
  "asctime": "2024-01-26 10:30:45",
  "name": "api",
  "levelname": "INFO",
  "message": "API call successful: GET /products"
}
```

## 🔧 Configuration

### Prometheus Configuration
`monitoring/prometheus.yml` faylida konfiguratsiya

### Loki Configuration
`monitoring/loki.yml` faylida konfiguratsiya

### Grafana Dashboards
`monitoring/grafana/dashboards/` papkasida

## 📊 Grafana Dashboard

Dashboard quyidagi panellarni o'z ichiga oladi:

1. **API Requests per Second** - Soniyada API so'rovlar
2. **Response Time** - Javob vaqti (95th va 50th percentile)
3. **System CPU Usage** - CPU foydalanish
4. **System Memory Usage** - Xotira foydalanish
5. **Active Orders** - Faol buyurtmalar
6. **Products Count** - Mahsulotlar soni
7. **Application Logs** - Ilova loglari

## 🚨 Alerting

Grafana orqali alert qo'yish mumkin:

- CPU usage > 80%
- Memory usage > 90%
- API response time > 2s
- Error rate > 5%

## 🔍 Troubleshooting

### Agar Prometheus metrics ko'rinmasa:
1. `/metrics` endpoint ishlayotganini tekshiring
2. Prometheus configuration to'g'riligini tekshiring
3. Network connectivity ni tekshiring

### Agar Loki logs ko'rinmasa:
1. `logs/` papkasi mavjudligini tekshiring
2. Promtail konfiguratsiyasini tekshiring
3. Log file permissions ni tekshiring

## 📚 API Examples

### Mahsulot yaratish:
```bash
curl -X POST http://localhost:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Olma", "price": 5.50}'
```

### Buyurtma berish:
```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Ali Valiyev",
    "phone": "+998901234567", 
    "address": "Tashkent, Uzbekistan",
    "items": [{"product_id": 1, "quantity": 3}]
  }'
```

### Statistika olish:
```bash
curl http://localhost:5000/api/v1/stats
```