# Firmware

Este proyecto se orienta a correr sobre sistemas Linux ligeros como Raspberry Pi o mini PC.

## Enfoque

- El firmware debe mantener el dispositivo en modo observador.
- No se debe activar ningún bloque de transmisión RF.
- Los registros deben contener solo metadatos mínimos (frecuencia, RSSI, duración, etiqueta).
- No se debe decodificar ningún payload privado.

## Requisitos básicos

- Python 3.11+
- Acceso local a los dispositivos Wi-Fi/BLE o SDR en modo RX
- Un servicio local ligero (FastAPI) para el dashboard

## Evolución prevista

- Fase 1: simulación local sin hardware SDR obligatorio.
- Fase 2: soporte de SDR básico con RTL-SDR.
- Fase 3: soporte avanzado para HackRF en modo RX-only.

## Seguridad

El firmware debe impedir expresamente funciones TX en perfiles SDR avanzados y respetar la política `RX_ONLY.md`.
