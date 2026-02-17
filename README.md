
# Traffic Labs - Edge Traffic Infrastructure

Набор лабораторных стендов вокруг одной архитектуры обработки трафика.
Основная цель проекта - показать не лендинги, а инфраструктуру вокруг
них: роутинг, проксирование, логические слои, наблюдаемость и
автоматизацию.
=======
# Traffic Labs from @trell

Основная идея — показать не отдельные сервисы, а архитектуру обработки трафика через несколько независимых слоёв: edge routing, decision layer и delivery layer.
Проект не про лендинги как продукт. Лендинги используются только как backend для демонстрации инфраструктурного поведения.

Проект не имитирует production полностью, но повторяет архитектурные
принципы, которые используются в edge-системах обработки трафика.

------------------------------------------------------------------------

## Архитектура

Трафик не попадает напрямую на лендинг. Он проходит через несколько
независимых слоёв:

Client ↓ Router (edge слой) ↓ Tracker (decision слой) ↓ Load Balancer
(delivery слой) ↓ Landing pool

Bot traffic → Safe Landing
=======
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

Каждый слой выполняет только одну задачу и не знает о внутренней логике
остальных.

------------------------------------------------------------------------

## Слои инфраструктуры

### Router --- Edge Layer

Первая точка входа.

Router принимает внешний трафик (порт 8085) и выполняет первичное
решение:
=======
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

-   анализ User-Agent
-   разделение bot / human
-   проксирование в tracker или safe landing

Router намеренно максимально простой. Он не занимается балансировкой и
не содержит бизнес-логики.

------------------------------------------------------------------------

### Tracker --- Decision Layer

Промежуточный логический слой между edge и delivery.

Задачи tracker:
=======
### Tracker

Decision слой.

* отделяет edge routing от delivery
* пишет decision-логи
* проксирует запросы в load balancer
* демонстрирует архитектуру multi-layer routing

-   логирование принятых решений
-   изоляция логики от router
-   проксирование трафика дальше

Tracker нужен, чтобы router оставался лёгким и не превращался в монолит.

------------------------------------------------------------------------

### Load Balancer --- Delivery Layer
=======
### Load Balancer

Delivery слой.

* round-robin между landing1 / landing2 / landing3
* не содержит логики фильтрации
* отвечает только за распределение нагрузки

Отвечает только за распределение нагрузки:

-   round-robin между landing контейнерами
-   никакой фильтрации
-   никакой логики bot/human

------------------------------------------------------------------------

### Landing Pool

Минимальные backend лендинги. Используются только как демонстрационные
сервисы.
=======
### Safe Landing

Fallback endpoint.

Используется для bot traffic и тестирования маршрутизации.

------------------------------------------------------------------------

### Safe Landing

Отдельный fallback endpoint для bot traffic и проверок.

------------------------------------------------------------------------

=======
### Monitoring

Monitoring вынесен в отдельный стек:

edge-stack != monitoring

Мониторинг не зависит от реализации роутинга и может использоваться
другими сервисами.

------------------------------------------------------------------------

## Control Plane --- Ansible

Ansible используется как единый источник истины.
=======
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

Он:

-   генерирует nginx конфиги из templates
-   генерирует docker-compose
-   управляет жизненным циклом инфраструктуры

deploy.yml → запуск\
stop.yml → остановка\
restart.yml → рестарт

Файлы внутри edge-stack считаются generated.
=======
## Что демонстрирует проект

* multi-layer nginx routing
* decision layer между edge и delivery
* fallback routing для bot traffic
* persistent logging через bind volumes
* сбор runtime метрик nginx через exporter
* отдельный monitoring стек
* авто-деплой через Ansible

------------------------------------------------------------------------

## Структура репозитория

traffic-labs/ ├── ansible/ │ ├── templates/ │ ├── group_vars/ │ ├──
deploy.yml │ ├── stop.yml │ ├── restart.yml │ └── inventory.ini │ ├──
edge-stack/ │ ├── landing/ │ ├── safe-landing/ │ ├── tracker/ │ ├──
logs/ │ ├── docker-compose.yml │ ├── router-nginx.conf │ └──
lb-nginx.conf │ ├── monitoring/ │ ├── docker-compose.yml │ └──
prometheus.yml │ └── README.md
=======
## Запуск

### Monitoring

------------------------------------------------------------------------

## Быстрый старт

Запуск всей инфраструктуры:
=======
```
Prometheus  — http://localhost:9090
Grafana     — http://localhost:3000
Exporter    — http://localhost:9113/metrics
```

ansible-playbook -i inventory.ini deploy.yml

Остановка:
=======
### Edge Stack

ansible-playbook -i inventory.ini stop.yml

Рестарт:

ansible-playbook -i inventory.ini restart.yml

------------------------------------------------------------------------

## Проверка роутинга
=======
### Авто-деплой

```
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
```

Playbook поднимает monitoring и edge-stack.

---

## Проверка маршрутизации

Human traffic:

curl -A "Mozilla" localhost:8085

Bot traffic:

curl -A "googlebot" localhost:8085

Mozilla → router → tracker → load balancer → landing\
googlebot → router → safe landing

------------------------------------------------------------------------
=======
Ожидаемый flow:

```
Mozilla  → Router → Tracker → LoadBalancer → Landing
googlebot → Router → Safe Landing
```

## Логи

edge-stack/logs/router/\
edge-stack/logs/tracker/\
edge-stack/logs/lb/

По логам можно восстановить полный flow запроса:

=======
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

------------------------------------------------------------------------

## Автор

tragic / @trell
=======


