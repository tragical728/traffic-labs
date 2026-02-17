# Инфраструктура для обработки трафика

Проект собран как набор лабораторных стендов вокруг одной архитектуры.
Главный фокус — инфраструктура и поведение прокси-цепочки.

---

### Общая схема

Трафик не идёт напрямую на лендинг.
Он проходит через несколько независимых слоёв:

```
Client
   ↓
Router (edge слой)
   ↓
Tracker (логический слой)
   ↓
Load Balancer
   ↓
Landing pool (landing1, landing2, landing3)

Bot-трафик
   └──→ Safe Landing
```

Каждый слой отвечает только за свою задачу.

---

### Назначение слоёв

## Router

Точка входа в систему.

* принимает входящий трафик (порт 8085)
* выполняет базовую фильтрацию по User-Agent
* ботов отправляет на safe landing
* обычные запросы проксирует в tracker

Router максимально простой и не содержит логики балансировки.

---

## Tracker

Логический слой между edge и доставкой.

Зачем он нужен:

* отделяет принятие решений от edge-роутера
* пишет decision-логи
* позволяет расширять логику без изменения router

Tracker получает запрос от router и решает, куда его отправить дальше.

---

## Load Balancer

Отвечает только за распределение нагрузки.

* round-robin между landing контейнерами
* не знает ничего о ботах или фильтрации
* выполняет роль delivery слоя

---

## Safe Landing

Отдельный fallback endpoint.

Используется для:

* bot traffic
* проверок
* резервного ответа

---

## Monitoring

Prometheus и Grafana вынесены в отдельный стек.

Это сделано специально, чтобы показать разделение инфраструктуры:

```
edge-stack != monitoring
```

Мониторинг не зависит от конкретной реализации роутинга.

---

### Структура репозитория

```
traffic-labs/
├── ansible/        # примеры автоматизации
├── edge-stack/
│   ├── landing/
│   ├── safe-landing/
│   ├── tracker/
│   ├── logs/       # runtime логи (не коммитятся)
│   ├── docker-compose.yml
│   ├── router-nginx.conf
│   └── lb-nginx.conf
├── monitoring/
│   ├── docker-compose.yml
│   └── prometheus.yml
└── README.md
```

---

### Что здесь демонстрируется

* цепочка reverse proxy из нескольких nginx
* разделение edge / logic / delivery слоёв
* decision logging
* fallback routing
* постоянные логи через bind volumes
* базовая observability через Prometheus и Grafana

Лендинги здесь минимальные — они нужны только для демонстрации инфраструктуры.

---

### Запуск

## 1. Мониторинг

```
cd monitoring
docker compose up -d
```

Доступ:

* Prometheus — http://localhost:9090
* Grafana — http://localhost:3000

---

## 2. Edge Stack

```
cd edge-stack
docker compose up -d --build
```

Точка входа:

```
http://localhost:8085
```

---

### Проверка работы роутинга

Обычный запрос:

```
curl -A "Mozilla" localhost:8085
```

Бот:

```
curl -A "googlebot" localhost:8085
```

Ожидаемое поведение:

* Mozilla → router → tracker → load balancer → landing pool
* googlebot → router → safe landing

---

### Логи

Каждый слой пишет собственные access-логи:

```
edge-stack/logs/router/
edge-stack/logs/tracker/
edge-stack/logs/lb/
```

Логи показывают не просто HTTP-доступ, а путь запроса через инфраструктуру.

По ним можно восстановить полный flow:

```
ROUTER → TRACKER → LB → LANDING
```

---

### Почему добавлен Tracker

Tracker — это отдельный логический слой.

Он нужен для того, чтобы:

* не перегружать router сложной логикой
* централизовать decision routing
* иметь отдельные логи принятых решений

Такую модель часто используют в edge-инфраструктурах, где routing развивается со временем.

---

###  Спасибо за внимание
### Усердно made by @trell 
