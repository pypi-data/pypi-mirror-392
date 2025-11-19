from enum import Enum


class ListJobsTriggerKind(str, Enum):
    CLI = "cli"
    DEFAULT_EMAIL = "default_email"
    EMAIL = "email"
    GCP = "gcp"
    HTTP = "http"
    KAFKA = "kafka"
    MQTT = "mqtt"
    NATS = "nats"
    POLL = "poll"
    POSTGRES = "postgres"
    SCHEDULE = "schedule"
    SQS = "sqs"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"

    def __str__(self) -> str:
        return str(self.value)
