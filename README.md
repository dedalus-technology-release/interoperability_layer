# Interoperability Layer – Project Overview

## Interoperability Concept

According to IEEE, interoperability is "the ability of two or more systems or components to exchange information and to use the information that has been exchanged."

This project emphasizes **semantic interoperability**, allowing various system components to:
- Access shared data through a common vocabulary (e.g., using standard URIs like `https://w3id.org/dco#Temperature`).
- Maintain their local terminology (e.g., `temperature`, `temperatura`, `temperatur`) while remaining interoperable.

## Architecture Overview

The system leverages a **FIWARE-based architecture** consisting of the following core components:

- **IoT Agent (NGSI-JSON)**: Receives device measurements via MQTT (in JSON) and converts them to NGSI-LD format.
- **Orion Context Broker (Orion-LD)**: Manages context data (entities, attributes, etc.) in NGSI-LD format.
- **MongoDB**: Stores IoT Agent and Context Broker data.
- **Mosquitto MQTT Broker**: Manages message exchange between devices and the IoT Agent.
- **HTTP Web Server**: Serves JSON-LD context files for data model semantics.


## MQTT Message Format
Devices publish their sensor data to MQTT topics with a specific pattern to enable the IoT Agent to properly route and process the data.

**Topic format:**
```
/json/<api-key>/<device-id>/attrs
```

**Example:**
```
/json/Project-Building4264/ws32158/attrs
```

**Payload example:**
```json
{
  "datetime": "2024-09-05T15:00:00.000000Z",
  "humidity": 61.33,
  "temperature": 25.13,
  "co2": 419.0,
  "batteryVoltage": 3.6
}
```
Each payload contains the timestamp (datetime) and sensor measurements. The IoT Agent listens on these topics and converts incoming data into NGSI-LD format.
## Docker Components
The system runs as Docker containers for easy deployment and management.

### MQTT Broker (Mosquitto)

- Connects devices and the IoT Agent using MQTT protocol.
- Can be configured to connect to a public broker or run locally.
- Example Mosquitto configuration includes subscribing to relevant topics, e.g.:
```yaml

connection remote_mosquitto
address test.mosquitto.org:1883
topic /json/Project-Building4264/# in
```

### IoT Agent Configuration

Exposed on port `4041`. Key environment variables:
```bash

IOTA_CB_HOST=orion                  # Context Broker hostname
IOTA_MQTT_HOST=mosquitto            # MQTT Broker hostname
IOTA_CB_NGSI_VERSION=ld             # Use NGSI-LD format
IOTA_JSON_LD_CONTEXT=http://context/ngsi-project-context.jsonld
IOTA_FALLBACK_TENANT=your_project
IOTA_FALLBACK_PATH=/your_project_path
```

### Context Broker (Orion-LD)

Runs on port `1026`, responsible for storing and updating NGSI-LD entities. Configuration includes:

```bash
-dbhost mongo-db
-db orionld
-logLevel DEBUG
```

### Web Server (Context Host)

Run on port `3004`. Serves JSON-LD context files that define the semantic data model, enabling clients to understand attribute meanings.
```
http://context/ngsi-project-context.jsonld
```

### MongoDB

Stores all provisioning and context data. Runs on port `27017`.

## Provisioning Examples
This section demonstrates how to provision entities, services, and devices in the FIWARE ecosystem.

## Context File Example (`ngsi-project-context.jsonld`)
Defines the semantic context used across the system, mapping attribute names to standardized URIs:
```json
{
  "@context": {
    "type": "@type",
    "id": "@id",
    "ngsi-ld": "https://uri.etsi.org/ngsi-ld/",
    "fiware": "https://uri.fiware.org/ns/dataModels#",
    "schema": "https://schema.org/",
    "Building": "https://w3id.org/dco#Building",
    "Device": "https://w3id.org/dco#Device",
    "temperature": "https://w3id.org/dco#Temperature",
    "humidity": "https://w3id.org/dco#Humidity",
    "co2": "https://w3id.org/dco#CO2Concentration",
    "batteryVoltage": "https://w3id.org/dco#BatteryVoltage",
    "controlledAsset": "fiware:controlledAsset",
    "dateObserved": "http://www.w3.org/2001/XMLSchema#date"
  }
}
```

### Building Entity
Create a building entity in the Context Broker with semantic attributes for address and location:

```http
POST http://localhost:1026/ngsi-ld/v1/entities/
Headers:
  fiware-service: your-project
  fiware-servicepath: /your-project-servicepath
  Content-Type: application/json
  Link: <http://context/ngsi-project-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"

Payload:
{
  "id": "urn:ngsi-ld:Building:Building4264",
  "type": "Building",
  "address": {
    "type": "Property",
    "value": {
      "streetAddress": "Example Street 17",
      "addressRegion": "Region",
      "addressLocality": "City",
      "postalCode": "0000"
    }
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [0.000000, 0.000000]
    }
  },
  "name": {
    "type": "Property",
    "value": "Building4264"
  }
}
```

### Device Entity
Associate a device with the building entity, enabling its measurements to be linked to a specific asset:
```http
POST http://localhost:1026/ngsi-ld/v1/entities/
Headers: same as above

Payload:
{
  "id": "urn:ngsi-ld:Device:ws32158",
  "type": "Device",
  "name": {"type": "Property", "value": "ws32158"},
  "controlledAsset": {
    "type": "Relationship",
    "object": ["urn:ngsi-ld:Building:Building4264"]
  }
}
```

### Service Group Provisioning
Register a service group in the IoT Agent, linking API keys to the Context Broker and entity types:
```http
POST http://localhost:4041/iot/services
Headers: same as above
Payload:
{
  "services": [
    {
      "apikey": "Project-Building4264",
      "cbroker": "http://orion:1026",
      "entity_type": "Device",
      "resource": ""
    }
  ]
}
```

### Device Provisioning
Configure the device in the IoT Agent, defining its protocol, transport, attributes, and timezone:
```http
POST http://localhost:4041/iot/devices
Headers:
  fiware-service: project
  fiware-servicepath: /building4264
Payload:
{
  "devices": [
    {
      "device_id": "ws32158",
      "entity_name": "urn:ngsi-ld:Device:ws32158",
      "entity_type": "Device",
      "apikey": "Project-Building4264",
      "protocol": "IoTA-JSON",
      "transport": "MQTT",
      "timezone": "Europe/Berlin",
      "explicitAttrs": [
        "temperature", "humidity", "co2", "batteryVoltage", "dateObserved", "unitCode"
      ],
      "attributes": [
        {"object_id": "datetime", "name": "dateObserved", "type": "Property"},
        {"object_id": "temperature", "name": "temperature", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "CEL"}}},
        {"object_id": "humidity", "name": "humidity", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "P1"}}},
        {"object_id": "co2", "name": "co2", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "KGM"}}},
        {"object_id": "batteryVoltage", "name": "batteryVoltage", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "VLT"}}}
      ]
    }
  ]
}
```



## Interoperability Levels

1. **Device Level**: Each device can use its native terminology while remaining compatible with the system via configured transformation rules.
2. **IoT Agent Level**: Attribute mapping during provisioning ensures correct transformation to NGSI-LD format.
3. **Context Broker Level**: Context files allow external stakeholders to understand the data model in a consistent and multilingual way.

## Example Use Case

Multiple deployments (e.g., in different countries) can:
- Use localized context files for internal data management.
- Maintain external semantic alignment via standard URIs and context definitions.
