# Arquitectura

Agentes principales:

- `sensor_rf_agent`: fuente abstracta de eventos RF. Implementa un simulador en `sources/`.
- `detector_agent`: heurísticas de clasificación (no-ML).
- `correlation_agent`: correlaciona eventos en ventana temporal.
- `alert_agent`: convierte probabilidad agregada en nivel de alerta.
- `legal_logging_agent`: registra metadatos mínimos en SQLite.
