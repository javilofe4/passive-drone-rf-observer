# passive-drone-rf-observer

Observador RF pasivo para detectar actividad compatible con drones cercanos.

IMPORTANTE: Este proyecto implementa únicamente observación pasiva. No transmite, no interfiere, no decodifica comunicaciones privadas ni intenta localizar personas o pilotos. Revise la normativa local antes de usar.

Qué hace:
- Simula fuentes RF y procesa eventos.
- Clasifica eventos con heurísticas simples.
- Correlaciona eventos cercanos en el tiempo.
- Emite alertas locales por consola y guarda logs mínimos.

Qué NO hace:
- No transmite ni realiza jamming/spoofing/deauth.
- No decodifica payloads privados.
- No intenta identificar o rastrear personas.

Instalación rápida (Linux / Raspberry Pi):

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Ejecutar la simulación:

```bash
python -m passive_drone_rf_observer
```

Ejecutar el dashboard local:

```bash
python -m uvicorn passive_drone_rf_observer.api.app:app --reload --host 127.0.0.1 --port 8000
```

Si usas un entorno virtual, asegúrate de activarlo primero o usa el Python del entorno.

Abrir `http://127.0.0.1:8000` en el navegador.

Correr tests:

```bash
pytest -q
```

Arquitectura (agents):
- `sensor_rf_agent` — fuente abstracta de eventos RF (incluye simulador).
- `detector_agent` — heurísticas de clasificación (noise, wifi_like, drone_like, unknown).
- `correlation_agent` — agrupa eventos en ventana temporal y calcula probabilidad agregada.
- `alert_agent` — emite alertas locales (none, low, medium, high).
- `legal_logging_agent` — guarda logs mínimos, sin payloads ni datos personales.

Perfiles de hardware:
- `simulated`
- `wifi_ble_remote_id`
- `rtl_sdr_v4`
- `hackrf_rx_only`

Configuración por defecto:
- `RX_ONLY=true`
- `ENABLE_SDR=false`
- `ENABLE_REMOTE_ID=false`
- `ENABLE_WIFI_MONITOR=false`
- `ENABLE_HACKRF=false`

Ver `docs/hardware.md`, `docs/firmware.md` y `RX_ONLY.md`.

Roadmap:
- Fase 1: Simulador (esta versión)
- Fase 2: Integración SDR pasiva (RTL-SDR, HackRF)
- Fase 3: Dashboard local
- Fase 4: Remote ID (si legalmente viable)
- Fase 5: Antena direccional y estimación de dirección

Ver `docs/` para más detalles sobre límites legales y arquitectura.
