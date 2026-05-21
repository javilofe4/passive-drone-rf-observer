# Hardware

El proyecto define tres perfiles de hardware compatibles con la filosofía de observación pasiva.

## 1. Perfil mínimo

- Raspberry Pi o mini PC
- Modo monitor Wi-Fi
- Bluetooth/BLE
- No requiere SDR para comenzar
- Ideal para pruebas locales y detección de actividad RF a nivel de infraestructura general

## 2. Perfil SDR básico

- RTL-SDR Blog V4
- Recepción pasiva en bandas sub-GHz
- Registra metadatos como frecuencia, RSSI y duración
- No implementa transmisión RF
- Buen punto de partida para añadir sensores de RF externos sin complejidad de TX

## 3. Perfil SDR avanzado

- HackRF One u otro SDR compatible 1 MHz–6 GHz
- Uso exclusivo de RX
- La configuración y la documentación deben dejar claro que no se usa TX
- Análisis de energía en bandas 2.4 GHz y 5.8 GHz
- Sin decodificación de payloads privados

## Perfiles disponibles

- `simulated`
- `wifi_ble_remote_id`
- `rtl_sdr_v4`
- `hackrf_rx_only`

## Nota

El código inicial prepara la estructura para estos perfiles, pero aún no implementa drivers SDR complejos. El objetivo es mantener la base clara y extensible.
