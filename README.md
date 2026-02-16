# Traffic Infrastructure Lab

Production-like лаборатория инфраструктуры для высоконагруженного трафика.

Репозиторий разделён на независимые лабы, каждая из которых показывает отдельный инфра уровень.

---

# 🧱 Архитектура репозитория

```
traffic-infrastructure-lab
│
├── 01-load-balancer   → Multi-container инфраструктура + мониторинг
└── 02-smart-router    → Умный роутинг трафика + backup landing
```

---

# 🔥 Labs

---

## 01 — Nginx Load Balancer Infrastructure

Production-like инфраструктура балансировки трафика.

### Архитектура

```
Client Request
      ↓
   Nginx LB (Port 8080)
      ↓
   ┌──────┴──────┬──────────┐
   ↓             ↓          ↓
Landing1     Landing2   Landing3...
   ↓             ↓          ↓
nginx-exporter → Prometheus → Grafana
```

### Возможности

* Docker контейнеризация лендингов
* Nginx upstream load balancing
* Авто-деплой новых лендингов
* Prometheus + Grafana мониторинг
* Масштабируемая архитектура

### Стек

* Docker / Docker Compose
* Nginx (Alpine)
* Prometheus
* Grafana
* Python (auto deploy script)

---

## 02 — Smart Traffic Router

Лаборатория умного reverse proxy routing.

### Архитектура

```
Client
   ↓
Nginx Smart Router
   ↓            ↓
Main Landing   Backup Landing
```

### Что демонстрируется

* Routing по User-Agent
* Backup fallback логика
* Reverse proxy chaining
* Access logs (IP + UA + upstream)
* Docker network isolation

### Основная идея

Router принимает входящий трафик и принимает решение:

* бот → backup landing
* обычный пользователь → основной поток

---

# 🚀 Быстрый старт

## Требования

* Docker Desktop
* Python 3.x

---

## Запуск 01-load-balancer

```
cd 01-load-balancer
docker compose up -d --build
```

Доступ:

* Лендинги: http://localhost:8080
* Prometheus: http://localhost:9090
* Grafana: http://localhost:3000

---

## Запуск 02-smart-router

```
cd 02-smart-router
docker compose up -d --build
```

Доступ:

* Router: http://localhost:8081

---

# ⚙️ Авто-деплой лендинга (01-lab)

```
python auto-deploy.py landing5
```

Скрипт автоматически:

* создаёт новый контейнер
* обновляет upstream
* пересобирает инфраструктуру
* обновляет мониторинг

---

# 📊 Мониторинг

### Grafana

1. http://localhost:3000
2. admin / admin
3. Prometheus datasource:

```
http://prometheus:9090
```

Можно использовать dashboard ID: 12708

### Ключевые метрики

* Requests per second
* Active connections
* Upstream status
* Traffic distribution

---

# 🧠 Цель проекта

Репозиторий показывает постепенную эволюцию DevOps-инфраструктуры:

```
01 → Load Balancer + Monitoring
02 → Smart Router + Traffic Routing
```

Фокус — на инфраструктуре вокруг traffic systems, а не на самих трекерах.
---

# 👤 Автор

tragic TG — @trell
