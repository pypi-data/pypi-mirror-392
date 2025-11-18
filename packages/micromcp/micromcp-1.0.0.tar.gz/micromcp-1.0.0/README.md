# microMCP
Eine extrem leichtgewichtige, FastMCP-kompatible Model Context Protocol (MCP) Server-Bibliothek
für MicroPython (z.B. ESP32).  
Das Hauptmerkmal ist, dass es keine externen Abhängigkeiten benötigt. 
> Aktuell wird ausschließlich der StreamableHttpTransport aus der fastMCP Bibliothek unterstützt.

## Features 
- FastMCP-ähnliche Decorator-API (@mcp.tool, @mcp.resource).
- Integrierter, minimaler WebSocket-Server (keine Abhängigkeiten). 
- Implementiert JSON-RPC 2.0 für die MCP-Kommunikation.
- Extrem schlank für den Einsatz auf ESP32. 

## Installation
Du kannst die Bibliothek direkt auf deinem MicroPython-Board über mip (den modernen upip-Nachfolger) installieren, 
sobald sie auf PyPI veröffentlicht ist:
```python
import mip
mip.install("micromcp")
```
Oder manuell: Kopiere einfach das Verzeichnis micromcp/ in das lib/-Verzeichnis auf deinem Gerät.  

Beispiel-Verwendung (z.B. main.py auf ESP32)
```python
import network
import utime
from micromcp import MicroMCPServer

# --- 1. WLAN verbinden (Voraussetzung) ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Verbinde mit WLAN...')
    wlan.connect('DEINE_SSID', 'DEIN_PASSWORT')
    while not wlan.isconnected():
        utime.sleep(1)
print('Netzwerk-Konfiguration:', wlan.ifconfig())

# --- 2. microMCP Server instanziieren ---
# Der Host 0.0.0.0 bindet an die IP des ESP32
mcp = MicroMCPServer(name="ESP32_Wohnzimmer", host='0.0.0.0', port=8080)

# --- 3. Tools und Ressourcen definieren ---

@mcp.tool
def get_system_uptime() -> dict:
    """Gibt die System-Laufzeit in Millisekunden zurück."""
    return {"uptime_ms": utime.ticks_ms()}

@mcp.tool
def add(a: int, b: int) -> int:
    """Addiert zwei Zahlen (FastMCP Kompatibilitätstest)."""
    return a + b

@mcp.resource("config://version")
def get_version():
    """Gibt die Firmware-Version zurück."""
    return {"version": "1.0.0-beta"}

# --- 4. Server in einem Thread starten ---
if __name__ == "__main__":
    mcp.run_threaded()
    
    # Haupt-Thread kann andere Dinge tun (z.B. LED blinken lassen)
    print("MCP Server läuft im Hintergrund...")
    while True:
        utime.sleep(10)
```


## Kompatibilität

Getestet für die Verbindung mit einem Standard fastmcp Python-Client.
```python
# coding:utf-8
"""Simple test script to test micromcp compatibility with fastmcp"""
# client.py (auf deinem Laptop)
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

TOKEN = "token"

async def main():
    # Übergib die 'Host:Port'-Adresse und die Transport-Klasse
    transport = StreamableHttpTransport(
        url="http://192.168.0.219:8080/mcp",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "X-Custom-Header": "value"
        }
    )
    async with Client(transport=transport) as client:

        print("Warte auf client.list_tools()...")
        tools = await client.list_tools()
        print(f"Verfügbare Tools: {tools}")

        resources = await client.list_resources()
        print(f"Verfügbare Ressourcen: {resources}")

        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Ergebnis von add(5, 3): {result.content}")

        result_uptime = await client.call_tool("get_system_uptime", {})
        print(f"ESP32 Uptime: {result_uptime.content}")

        version = await client.read_resource("config://version")
        print(f"ESP32 version: {version}")


if __name__ == "__main__":
    asyncio.run(main())

```

