# Инфраструктурный стенд обработки трафика 
##TG - @trell

Этот репозиторий — набор лабораторных стендов, посвящённых инфраструктуре обработки HTTP-трафика.
Основная цель проекта — показать, как можно собрать многоуровневую цепочку reverse-proxy, разделить зоны ответственности между сервисами и добавить наблюдаемость через метрики и логи.

Проект не про лендинги как продукт. Лендинги здесь используются только как демонстрационные backend-сервисы.

---

## Общая архитектура

Трафик проходит через несколько независимых слоёв:

```
Client
   ↓
Router (edge слой)
   ↓
Tracker (decision слой)
   ↓
Load Balancer
   ↓
Landing pool (landing1, landing2, landing3)

Bot traffic
   └──→ Safe Landing
```

Отдельно работает monitoring стек:

```
Prometheus + Grafana + nginx exporter
```

---

## Назначение слоёв

### Router

Edge-точка входа.

* слушает порт 8085
* выполняет базовую фильтрацию по User-Agent
* ботов отправляет на safe landing
* обычный трафик проксирует в tracker
* отдаёт nginx stub_status для сбора метрик

Router intentionally простой — логика не смешивается с балансировкой.

---

### Tracker

Логический слой.

Задачи:

* отделяет edge routing от delivery
* пишет decision-логи
* проксирует запросы в load balancer
* демонстрирует слой принятия решений внутри инфраструктуры

---

### Load Balancer

Delivery слой.

* round-robin между landing1 / landing2 / landing3
* не содержит логики фильтрации
* показывает распределение нагрузки

---

### Safe Landing

Fallback endpoint.

Используется для:

* bot traffic
* резервных ответов
* тестирования маршрутизации

---

### Monitoring Stack

Monitoring вынесен в отдельную директорию и запускается отдельно от edge-stack.

Используются:

* Prometheus
* Grafana
* nginx-prometheus-exporter

Exporter собирает метрики напрямую из Router через `/nginx_status`.

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

* многоуровневый nginx routing
* разделение edge / decision / delivery слоёв
* fallback routing
* persistent logging через bind volumes
* сбор runtime метрик nginx
* отдельный monitoring стек
* простой infra auto-deploy через Ansible

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

### Авто-деплой через Ansible

Из корня проекта:

```
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
```

Playbook поднимает monitoring и edge-stack.

---

## Проверка роутинга

Human traffic:

```
curl -A "Mozilla" localhost:8085
```

Bot traffic:

```
curl -A "googlebot" localhost:8085
```

Ожидаемое поведение:

* Mozilla → Router → Tracker → LoadBalancer → Landing pool
* googlebot → Router → Safe Landing

---

## Логи

Каждый слой пишет отдельные access-логи:

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

## Метрики и Grafana Dashboard

Router отдаёт nginx stub_status, который собирает nginx-exporter.

Prometheus забирает метрики exporter и Grafana отображает их через dashboard:

```
Grafana Dashboard ID: 12708
```

Доступны метрики:

* active connections
* requests/sec
* reading / writing / waiting
* nginx load

---

## Почему добавлен Tracker

Tracker — отдельный decision слой между edge и delivery.

Он нужен для:

* изоляции логики маршрутизации
* централизованных decision-логов
* расширяемости архитектуры без изменения Router

---

## Назначение проекта

Этот репозиторий — лабораторный стенд, демонстрирующий подход к построению edge-инфраструктуры:

* reverse proxy chain
* traffic filtering
* layered nginx routing
* observability через метрики и логи
* разделение инфраструктурных ролей

Это не production-решение, а инфраструктурный демо-проект.
