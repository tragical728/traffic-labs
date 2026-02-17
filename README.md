# Traffic Labs from @trell

Основная идея — показать не отдельные сервисы, а архитектуру обработки трафика через несколько независимых слоёв: edge routing, decision layer и delivery layer.
Проект не про лендинги как продукт. Лендинги используются только как backend для демонстрации инфраструктурного поведения.

---

## Архитектурный обзор

Вместо одного reverse-proxy используется цепочка сервисов с разделённой ответственностью:

```
Client
   ↓
Router (Edge Layer)
   ↓
Tracker (Decision Layer)
   ↓
Load Balancer (Delivery Layer)
   ↓
Landing Pool

Bot traffic
   └──→ Safe Landing
```

Отдельно работает monitoring стек:

```
nginx-exporter → Prometheus → Grafana
```

---

## Почему архитектура разбита на слои

В реальных traffic-системах edge routing, логика решений и доставка трафика часто разделяются.
Этот проект повторяет подобный подход в упрощённом виде.

* Router — точка входа и первичная фильтрация
* Tracker — логический слой, принимающий решения о маршрутизации
* Load Balancer — отвечает только за распределение нагрузки
* Monitoring — вынесен отдельно, чтобы не смешивать observability с routing

Такой подход упрощает развитие инфраструктуры и позволяет масштабировать слои независимо.

---

## Назначение компонентов

### Router

Edge слой.

* принимает входящий трафик (порт 8085)
* фильтрует User-Agent
* направляет ботов на safe landing
* передаёт основной трафик в tracker
* отдаёт `/nginx_status` для exporter

---

### Tracker

Decision слой.

* отделяет edge routing от delivery
* пишет decision-логи
* проксирует запросы в load balancer
* демонстрирует архитектуру multi-layer routing

---

### Load Balancer

Delivery слой.

* round-robin между landing1 / landing2 / landing3
* не содержит логики фильтрации
* отвечает только за распределение нагрузки

---

### Safe Landing

Fallback endpoint.

Используется для bot traffic и тестирования маршрутизации.

---

### Monitoring

Monitoring вынесен в отдельный стек:

* nginx-prometheus-exporter
* Prometheus
* Grafana

Exporter собирает метрики Router через `/nginx_status`.

Используется Grafana dashboard:

```
ID: 12708
```

---

## Структура репозитория

```
traffic-labs/
├── ansible/              # авто-деплой инфраструктуры
├── edge-stack/
│   ├── landing/
│   ├── safe-landing/
│   ├── tracker/
│   ├── logs/             # runtime логи (игнорируются git)
│   ├── router-nginx.conf
│   ├── lb-nginx.conf
│   └── docker-compose.yml
├── monitoring/
│   ├── docker-compose.yml
│   └── prometheus.yml
└── README.md
```

---

## Что демонстрирует проект

* multi-layer nginx routing
* decision layer между edge и delivery
* fallback routing для bot traffic
* persistent logging через bind volumes
* сбор runtime метрик nginx через exporter
* отдельный monitoring стек
* авто-деплой через Ansible

---

## Запуск

### Monitoring

```
cd monitoring
docker compose up -d
```

Доступ:

```
Prometheus  — http://localhost:9090
Grafana     — http://localhost:3000
Exporter    — http://localhost:9113/metrics
```

---

### Edge Stack

```
cd edge-stack
docker compose up -d --build
```

Точка входа:

```
http://localhost:8085
```

---

### Авто-деплой

```
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
```

Playbook поднимает monitoring и edge-stack.

---

## Проверка маршрутизации

Human traffic:

```
curl -A "Mozilla" localhost:8085
```

Bot traffic:

```
curl -A "googlebot" localhost:8085
```

Ожидаемый flow:

```
Mozilla  → Router → Tracker → LoadBalancer → Landing
googlebot → Router → Safe Landing
```

---

## Логи

Каждый слой пишет собственные access-логи:

```
logs/router/
logs/tracker/
logs/lb/
```

Логи показывают путь запроса через инфраструктуру:

```
ROUTER → TRACKER → LB → LANDING
```

---

