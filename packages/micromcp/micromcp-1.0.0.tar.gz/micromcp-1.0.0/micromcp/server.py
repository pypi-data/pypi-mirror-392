# -*- coding: utf-8 -*-
"""
microMCP: Eine leichtgewichtige, FastMCP-kompatible Model Context Protocol (MCP)
Server-Bibliothek für MicroPython, optimiert für StreamableHttpTransport.
"""

import usocket as socket
import json
import _thread
import utime as time
import select

# Das ist dein "Passwort". Der Client muss dies als Bearer-Token senden.
TOKEN = "token"


class MicroMCPServer:
    """
    Implementiert den MCP-Server-Kern für FastMCP StreamableHttpTransport.
    Verwendet eine HTTP/SSE (Server-Sent Events) Verbindung.
    """

    def __init__(self, name: str, host: str = '0.0.0.0', port: int = 8080):
        self._name = name
        self._host = host
        self._port = port
        self._tools = []  # Gesammelte Tool-Schemata
        self._methods = {}  # Registrierte Python-Funktionen
        self._resources = {}  # Registrierte Ressourcen
        self._resource_specs = [] # Gesammelte Resource-Schemata
        self._server_socket = None

        # Registriere das 'initialize' Tool automatisch beim Start
        function_spec = {
            "name": "initialize",
            "description": "Der Handshake für StreamableHttpTransport.",
            "inputSchema": {"type": "object", "properties": {}, "required": []},  # <- Korrigiert
        }
        self._register_tool_or_resource(function_spec, self.initialize, is_tool=True)

        print(f"MicroMCP '{self._name}' initialisiert auf http://{host}:{port}")

    # --- Decorator-Funktionen (Benutzer-API) ---

    def tool(self, func):
        """Decorator für MCP-Tool-Funktionen."""
        function_spec = {
            "name": func.__name__,
            "description": getattr(func, '__doc__', 'Keine Beschreibung verfügbar'),  # todo: das kann nicht so bleiben
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        }
        self._register_tool_or_resource(function_spec, func, is_tool=True)
        return func

    def resource(self, uri_pattern: str):
        """Decorator für MCP-Resource-Funktionen."""

        def decorator(func):
            function_spec = {
                "name": uri_pattern,  # Die URI ist der Name
                "description": getattr(func, '__doc__', 'Keine Beschreibung verfügbar'),  # todo: das kann nicht so bleiben
                "uri": uri_pattern,
                "uri_pattern": uri_pattern,
                "readSchema": {"type": "object", "properties": {}, "required": []},
                # Ähnlich wie inputSchema, aber für Ressourcen
                "outputSchema": {"type": "object", "properties": {}, "required": []},
            }
            self._register_tool_or_resource(function_spec, func, is_tool=False)
            return func

        return decorator

        # --- Eingebautes 'initialize' Tool ---

    @staticmethod
    def initialize(**kwargs):
        """
        Der Handshake für StreamableHttpTransport.
        Akzeptiert beliebige Parameter vom Client (z.B. protocolVersion, capabilities).
        """
        # Wir können session_id, falls vorhanden, aus den kwargs extrahieren
        session_id = kwargs.get('session_id')

        server_info = {
            "name": "ESP32_Wohnzimmer",  # TODO: Dies dynamisch machen
            "description": "MicroMCP Server auf ESP32",
            "vendor": "MicroMCP Project",
            "version": "v0.1.0"
        }
        capabilities = {
            "clientFeatures": {},
            "serverFeatures": {
                "authentication": True,
                "resourceResolution": True,
                "toolDiscovery": True,
                "streaming": True
            }
        }
        full_response = {
            "protocolVersion": "2025-06-18",  # die version von fastMCP
            "serverInfo": server_info,
            "capabilities": capabilities,
            # session_id wird jetzt aus kwargs genommen
            "session_id": session_id if session_id else None,
            "status": "ok"
        }
        return full_response

    # --- Interne Registrierung ---

    def _register_tool_or_resource(self, spec: dict, func_to_call, is_tool: bool):
        """Interne Registrierungslogik."""
        name = spec["name"]
        if is_tool:
            self._tools.append(spec)  # Vereinfacht, nur das Tool-Spec speichern
            self._methods[name] = func_to_call
        else:
            self._resources[spec['uri_pattern']] = func_to_call
            self._methods[name] = func_to_call
            self._resource_specs.append(spec)
        print(f"Registriert: {'Tool' if is_tool else 'Resource'} '{name}'")

    # --- JSON-RPC Protokoll-Logik ---

    def _create_rpc_response(self, result=None, error=None, rpc_id=None) -> bytes:
        """Erzeugt eine JSON-RPC-Antwort als UTF-8 Bytes."""
        response = {"jsonrpc": "2.0", "id": rpc_id}
        if error:
            response["error"] = error
        else:
            response["result"] = result
        return json.dumps(response).encode('utf-8')

    def _handle_rpc_request(self, request_json: dict) -> bytes | None:
        """Verarbeitet einen einzelnen JSON-RPC-Request oder eine Notification."""
        # Beispiel requests:
        # {"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"mcp","version":"0.1.0"}},"jsonrpc":"2.0","id":0}
        # {"method":"tools/call","params":{"name":"add","arguments":{"a":5,"b":3},"_meta":{"progressToken":2}},"jsonrpc":"2.0","id":2}
        rpc_id = request_json.get("id")
        rpc_json_version = request_json.get("jsonrpc")
        method = request_json.get("method")
        params = request_json.get("params", {})

        # 0. Handle Notification (Keine ID vorhanden)
        if rpc_id is None:
            print(f"DEBUG: Empfange Notification '{method}'. Keine Antwort erforderlich.")
            return None  # KEINE HTTP-Antwort senden

        if float(rpc_json_version) < 2.0:
            print(f"INFO: Client is using a different jsonrpc version. \nExpected: 2.0 \n Received: {rpc_json_version}")

        # 1. Handle Tool/Resource Discovery (list_tools, list_resources)
        if method in ["mcp.list_tools", "tools/list"]:
            print(f"DEBUG: Bearbeite '{method}' Anfrage.")
            return self._create_rpc_response(result={"tools": self._tools}, rpc_id=rpc_id)

        if method in ["mcp.list_resources", "resources/list"]:
            # Verwende die neue dedizierte Liste der Resource Specs
            print(f"DEBUG: Bearbeite '{method}' Anfrage. {len(self._resource_specs)} gefunden.")
            # FastMCP erwartet die Resource Specs direkt im 'resources' Schlüssel.
            return self._create_rpc_response(result={"resources": self._resource_specs}, rpc_id=rpc_id)

        # 2. Handle Tool Execution (tools/call)
        if method == "tools/call":

            tool_name = None
            tool_arguments = {}  # Variable umbenannt

            # 1. Tool-Namen bestimmen (liegt unter 'name')
            tool_name = params.get("name")

            # 2. Argumente bestimmen (liegt unter 'arguments' im FastMCP-Format)
            tool_arguments_raw = params.get("arguments")

            # 3. Wenn die Argumente gefunden wurden, verwende diese
            if isinstance(tool_arguments_raw, dict):
                tool_arguments = tool_arguments_raw
            else:
                # Fallback für die flache Struktur
                IGNORED_KEYS = ['tool_name', 'name', 'arguments', '_meta', 'params']
                tool_arguments = {k: v for k, v in params.items() if k not in IGNORED_KEYS}

            if not tool_name:
                error = {"code": -32602, "message": "Missing 'tool_name' in tools/call parameters"}
                return self._create_rpc_response(error=error, rpc_id=rpc_id)

            # 4. Tool ausführen
            if tool_name in self._methods:
                print(f"DEBUG: Führe über 'tools/call' Methode '{tool_name}' aus.")
                try:
                    tool_func = self._methods[tool_name]

                    # Meta-Argumente filtern
                    safe_args = {k: v for k, v in tool_arguments.items() if not k.startswith('_')}

                    result_data = tool_func(**safe_args)

                    # 1. Ergebnis in den 'TextContent'-Wrapper packen.
                    # Wir müssen explizit den Typ 'TextContent' angeben (FastMCP-Spezifikation).
                    # Die 'type' Felder MÜSSEN Literal-Strings sein ('text', 'image', etc.)
                    content_object = {
                        "__type__": "TextContent",  # Dies identifiziert den Typ eindeutig
                        "type": "text",  # Der MIME-Typ für Textinhalt
                        "text": str(result_data)  # Die eigentlichen Daten
                    }

                    # 2. Ergebnis-Objekt in eine Liste packen.
                    result_list = [content_object]

                    # 3. Finales Ergebnis in den 'content'-Wrapper packen.
                    final_result = {"content": result_list}
                    return self._create_rpc_response(result=final_result, rpc_id=rpc_id)
                except Exception as e:
                    print(f"FEHLER: Tool-Ausführungsfehler ({tool_name}): {e}")
                    error = {"code": -32000, "message": f"Tool-Ausführungsfehler ({tool_name}): {e}"}
                    return self._create_rpc_response(error=error, rpc_id=rpc_id)
            else:
                print(f"FEHLER: Tool '{tool_name}' nicht gefunden.")
                error = {"code": -32601, "message": f"Tool nicht gefunden: {tool_name}"}
                return self._create_rpc_response(error=error, rpc_id=rpc_id)

        # 2.5 Handle Resource Reading (resources/read)
        if method == "resources/read":
            # Erwarte die URI im 'uri' Schlüssel der params
            resource_uri = params.get("uri")
            resource_func = self._resources.get(resource_uri)

            if not resource_uri or not resource_func:
                print(f"FEHLER: Ressource '{resource_uri}' nicht gefunden.")
                error = {"code": -32601, "message": f"Ressource nicht gefunden: {resource_uri}"}
                return self._create_rpc_response(error=error, rpc_id=rpc_id)

            print(f"DEBUG: Führe über 'resources/read' Methode '{resource_uri}' aus.")

            try:
                # Die Resource-Funktion nimmt in der Regel keine Argumente entgegen,
                # da der Client alles via URI überträgt.
                result_data = resource_func()  # result_data ist {'version': '1.0.0-beta'}

                # Ergebnis in den Content-Wrapper packen (wie bei Tools)
                content_object = {
                    "__type__": "TextContent",
                    "type": "text",
                    "text": str(result_data),  # Muss string sein, da es ein TextContent ist
                    "uri": resource_uri
                    # FINAL KORRIGIERT: Füge die URI hinzu, da Resource-Content-Objekte dies benötigen
                }
                result_list = [content_object]

                # Key muss "contents" (Plural) sein.
                final_result = {"contents": result_list}
                return self._create_rpc_response(result=final_result, rpc_id=rpc_id)

            except Exception as e:
                print(f"FEHLER: Resource-Ausführungsfehler ({resource_uri}): {e}")
                error = {"code": -32000,
                         "message": f"Resource-Ausführungsfehler ({resource_uri}): Details im Server-Log."}
                return self._create_rpc_response(error=error, rpc_id=rpc_id)

        # 3. Handle Direct Method/Resource Call (Fallback, z.B. initialize, Resource-Aufrufe)
        if method in self._methods:
            print(f"DEBUG: Führe Methode '{method}' direkt aus (Nicht-Tool/Resource).")
            try:
                tool_func = self._methods[method]
                # Meta-Argumente wie '_meta' entfernen, falls direkt aufgerufen
                safe_params = {k: v for k, v in params.items() if not k.startswith('_')}

                result_data = tool_func(**safe_params)

                # Wichtig: Explizit die Antwort zurückgeben!
                return self._create_rpc_response(result=result_data, rpc_id=rpc_id)
            except Exception as e:
                # KORREKTUR: Sende eine statische Fehler-Nachricht zurück, um zu vermeiden,
                # dass die MicroPython-Laufzeitumgebung beim Serialisieren von f-strings mit Ausnahmen fehlschlägt.
                print(
                    f"FEHLER: Tool/Resource-Ausführungsfehler: {e}")  # Behalte detailliertes Logging im ESP32-Log
                error = {"code": -32000, "message": "Tool/Resource-Ausführungsfehler. Details im Server-Log."}
                return self._create_rpc_response(error=error, rpc_id=rpc_id)
        else:
            print(f"FEHLER: Methode '{method}' nicht gefunden.")
            error = {"code": -32601, "message": f"Methode/Resource nicht gefunden: {method}"}
            return self._create_rpc_response(error=error, rpc_id=rpc_id)

    # --- HTTP/SSE Server-Logik ---

    def _parse_http_headers_and_body(self, request_str: str) -> tuple[dict, str | None]:
        """
        Parst HTTP-Header und extrahiert den Body aus dem gesamten Request-String.
        Gibt (Headers-Dict, Body-String | None) zurück.
        """
        headers = {}
        body = None

        # 1. Body und Header trennen
        parts = request_str.split('\r\n\r\n', 1)
        header_part = parts[0]

        if len(parts) > 1:
            # Body existiert (alles, was nach der leeren Zeile kommt)
            body = parts[1].strip()

        # 2. Header parsen
        lines = header_part.split('\r\n')

        # Die erste Zeile ist die Request-Zeile (z.B. POST /mcp HTTP/1.1)
        # Wir speichern die Methode und den Pfad in den Headern für die spätere Nutzung
        if lines:
            request_line = lines[0].split(' ')
            if len(request_line) >= 2:
                headers[':method'] = request_line[0].upper()
                headers[':path'] = request_line[1]

        for line in lines[1:]:  # Überspringe die Request-Zeile
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value

        if 'application/json' in headers.get('content-type', '') and body:
            try:
                body = json.loads(body)
            except Exception:
                print("DEBUG: Fehler beim parsen des json bodys.")

        return headers, body

    def _serve_sse_mcp(self, client_socket):
        """
        Persistent HTTP/SSE-Schleife. Wartet auf POST-Requests und sendet SSE-Events.
        """
        print("DEBUG: Starte HTTP/SSE-Hauptschleife (warte auf POSTs)...")
        client_socket.setblocking(False)
        socket_list = [client_socket]

        while True:
            try:
                # 1. Warten auf Daten mit Timeout
                r, w, e = select.select(socket_list, [], [], 1)

                if not r:
                    # Timeout (1 Sekunde), nichts zu tun. Schleife läuft weiter.
                    continue

                # 2. Daten sind da, lese den POST-Request
                request_data = client_socket.recv(1024)
                if not request_data:
                    print("DEBUG: Client hat Verbindung in SSE-Schleife (sauber) geschlossen.")
                    break

                print(f"DEBUG: SSE-Schleife POST-Daten empfangen ({len(request_data)} Bytes).")

                # 3. HTTP-POST parsen
                try:
                    request_str = request_data.decode('utf-8')
                    parts = request_str.split('\r\n\r\n', 1)
                    if len(parts) < 2:
                        print("FEHLER: Unvollständiger POST-Request in Schleife.")
                        continue

                    header_str = parts[0]
                    payload_str = parts[1].strip()  # .strip() entfernt überflüssige Leerzeichen

                    if not header_str.startswith('POST'):
                        print(f"FEHLER: Unerwartete Methode in Schleife: {header_str.split(' ', 1)[0]}")
                        continue

                    if not payload_str:
                        print("DEBUG: Leerer POST-Body empfangen, ignoriere.")
                        continue

                except Exception as e:
                    print(f"FEHLER beim Parsen des POST-Requests: {e}")
                    continue

                # 4. RPC-Request verarbeiten
                try:
                    request_json = json.loads(payload_str)
                except ValueError:
                    print("FEHLER: JSON-Parse-Fehler im POST-Body.")
                    response_bytes = self._create_rpc_response(
                        error={"code": -32700, "message": "Parse error (HTTP body)"},
                        rpc_id=None
                    )
                else:
                    response_bytes = self._handle_rpc_request(request_json)

                # 5. RPC-Antwort als SSE-Event senden
                response_data = response_bytes.decode('utf-8')
                sse_response = f"data: {response_data}\r\n\r\n"
                client_socket.send(sse_response.encode('utf-8'))
                print("DEBUG: RPC-Antwort als SSE gesendet.")

            except Exception as e:
                print(f"FEHLER in SSE-Hauptschleife: {e}")
                break

        print("DEBUG: Verlasse SSE-Hauptschleife.")

    def _handle_connection(self, client_socket, client_addr):
        """
        Verwaltet die gesamte Lebensdauer einer einzelnen HTTP/SSE-Verbindung.
        """
        print(f"DEBUG: Neue Verbindung von {client_addr}")
        try:
            # 1. Ersten HTTP-Request (GET oder POST) blockierend lesen
            client_socket.setblocking(True)
            request_data = client_socket.recv(1024)
            if not request_data:
                print("DEBUG: Leere Anfrage, schließe Verbindung.")
                return

            request_str = request_data.decode('utf-8')
            print(f"DEBUG: Empfangener request_str: \n{request_str}")
            headers, body = self._parse_http_headers_and_body(request_str)
            print(f"DEBUG: Empfangene Header: {headers}")

            # 2. Autorisierung prüfen
            auth_header = headers.get('authorization', '')
            if auth_header != f"Bearer {TOKEN}":
                print(f"FEHLER: Auth fehlgeschlagen. Erwartet: 'Bearer {TOKEN}', Erhalten: '{auth_header}'")
                response = (
                    "HTTP/1.1 401 Unauthorized\r\n"
                    "WWW-Authenticate: Bearer realm=\"mcp_device\"\r\n"
                    "Connection: close\r\n\r\n"
                )
                client_socket.send(response.encode('utf-8'))
                return

            print("DEBUG: Auth erfolgreich.")

            # 3. Handshake-Antwort (200 OK + SSE-Header) senden
            response_header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/event-stream\r\n"
                "Cache-Control: no-cache\r\n"
                "Connection: keep-alive\r\n"
                "\r\n"
            )
            client_socket.send(response_header.encode('utf-8'))
            print("DEBUG: 200 OK SSE Header gesendet.")

            # Hole die Request-Methode aus den geparsten Headern
            request_method = headers.get(':method')

            # 4. 'initialize'-Antwort als ERSTES SSE-Event senden
            if body and request_method == 'POST':

                if isinstance(body, dict):
                    print("DEBUG: Verarbeite initialen POST-Body (JSON)...")
                    try:
                        # Der body ist das dict {"method":"initialize", "id":0, ...}
                        response_bytes = self._handle_rpc_request(body)

                        if response_bytes:
                            sse_event = f"data: {response_bytes.decode('utf-8')}\r\n\r\n"
                            client_socket.send(sse_event.encode('utf-8'))
                            print("DEBUG: Antwort auf initialen RPC-Call als SSE gesendet.")
                        else:
                            # Dies ist der Fall für Notifications (z.B. notifications/initialized)
                            print("DEBUG: RPC-Handler hat keine Antwort generiert (Notification ignoriert).")

                    except Exception as e:
                        print(f"FEHLER bei Verarbeitung des initialen RPC-Calls: {e}")
                        error_resp = self._create_rpc_response(
                            error={"code": -32000, "message": f"Initial RPC execution error: {e}"},
                            rpc_id=body.get("id")
                        )
                        sse_event = f"data: {error_resp.decode('utf-8')}\r\n\r\n"
                        client_socket.send(sse_event.encode('utf-8'))

                else:
                    print(f"FEHLER: Initialer POST-Body war kein valides JSON. Body war: {body}")
                    error_resp = self._create_rpc_response(
                        error={"code": -32700, "message": "Parse error (initial body was not valid JSON)"},
                        rpc_id=None
                    )
                    sse_event = f"data: {error_resp.decode('utf-8')}\r\n\r\n"
                    client_socket.send(sse_event.encode('utf-8'))

            # Hier ist die Zeile, die den Syntaxfehler verursacht hatte.
            elif request_method != 'POST':
                print(f"DEBUG: Initialer Request war ein {request_method}, kein POST. "
                      f"Warte auf RPC-Calls in der SSE-Schleife.")

            else:  # POST, aber 'body' war None oder leer
                print("DEBUG: Initialer POST-Request hatte keinen Body. Warte auf RPC-Calls in der SSE-Schleife.")

            # 5. Zur persistenten SSE-Schleife wechseln
            self._serve_sse_mcp(client_socket)

        except Exception as e:
            print(f"FEHLER in _handle_connection: {e}")

        finally:
            # Stelle sicher, dass der Socket immer geschlossen wird
            print(f"DEBUG: Verbindung zu {client_addr} wird geschlossen.")
            client_socket.close()

    # --- Server-Startfunktionen ---

    def run(self):
        """
        Startet den blockierenden, single-client MCP-Server.
        Dies ist der stabilste Modus für ESP32.
        """
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        addr = socket.getaddrinfo(self._host, self._port)[0][-1]
        self._server_socket.bind(addr)
        self._server_socket.listen(1)  # Nur 1 Client gleichzeitig

        print(f"\n=======================\n")
        print(f"Gesammelte Tool-Schemata: {self._tools}")
        print(f"Registrierte Python-Funktionen: {self._methods}")
        print(f"Registrierte Ressourcen: {self._resources}")
        print(f"\n=======================\n")

        print(f"MicroMCP '{self._name}' lauscht auf {addr}")

        while True:
            try:
                # Akzeptiere eine neue Verbindung (blockierend)
                client_socket, client_addr = self._server_socket.accept()

                # Bearbeite diesen einen Client, bis er fertig ist (blockierend)
                self._handle_connection(client_socket, client_addr)

                # Erst DANACH wird der nächste Client akzeptiert.

            except OSError as e:
                print(f"Socket Accept Fehler: {e}")
                time.sleep(1)

    def run_threaded(self) -> bool:
        """
        Startet den MCP-Server in einem separaten Thread.
        WARNUNG: Dies kann auf ESP32 zu 'OSError: 23' führen.
        """
        try:
            _thread.start_new_thread(self.run, ())
            print("MicroMCP-Server in separatem Thread gestartet.")
            return True
        except Exception as e:
            print(f"Fehler beim Starten des MCP-Threads: {e}")
            return False
