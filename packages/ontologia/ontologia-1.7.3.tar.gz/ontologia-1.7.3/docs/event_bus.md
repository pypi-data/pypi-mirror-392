# Event Bus Providers

Ontologia publishes domain events via an abstract `DomainEventBus`. The concrete
provider is selected from settings and can be swapped without changing business code.

## Providers

- in_process: default, in-memory, supports in-process handler subscriptions
- null: disabled bus (no-op)
- kafka: distributed event bus using Kafka (publish-only from core)

## Configuration

Set provider and Kafka options via settings (env vars or config file):

```bash
EVENT_BUS_PROVIDER=in_process           # or: kafka, null, disabled

# Kafka (only when EVENT_BUS_PROVIDER=kafka)
EVENT_BUS_KAFKA_BOOTSTRAP_SERVERS=localhost:9092
EVENT_BUS_KAFKA_TOPIC_PREFIX=ontologia
EVENT_BUS_KAFKA_CLIENT_ID=ontologia-api
EVENT_BUS_KAFKA_SECURITY_PROTOCOL=PLAINTEXT   # or SASL_SSL
EVENT_BUS_KAFKA_SASL_MECHANISM=PLAIN          # if SASL
EVENT_BUS_KAFKA_SASL_USERNAME=...
EVENT_BUS_KAFKA_SASL_PASSWORD=...
EVENT_BUS_SYNCHRONOUS_PUBLISH=false
```

## Handler Registration

- In-process only: Handlers register via `SubscribableEventBus` (subscribe/unsubscribe).
- Distributed (Kafka): Handlers should be wired in separate consumers/services.
