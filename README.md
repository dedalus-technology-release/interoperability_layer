# Interoperability Layer – Project Overview

## Table of Contents

- [Interoperability Concept](#interoperability-concept)
- [Architecture Overview](#architecture-overview)
- [MQTT Message Format](#mqtt-message-format)
- [Docker Components](#docker-components)
  - [MQTT Broker (Mosquitto)](#mqtt-broker-mosquitto)
  - [IoT Agent Configuration](#iot-agent-configuration)
  - [Context Broker (Orion-LD)](#context-broker-orion-ld)
  - [Web Server (Context Host)](#web-server-context-host)
  - [MongoDB](#mongodb)
- [Running the System with Docker Compose](#running-the-system-with-docker-compose)
- [Verify Running Services](#verify-running-services)
- [Provisioning Examples](#provisioning-examples)
  - [Context File Example (`ngsi-project-context.jsonld`)](#context-file-example-ngsi-project-contextjsonld)
  - [Building Entity Provisioning](#building-entity-provisioning)
  - [Device Entity Provisioning](#device-entity-provisioning)
  - [Service Group Provisioning](#service-group-provisioning)
  - [Device Provisioning](#device-provisioning)
  - [Summary – Device Provisioning Parameters Explained](#summary--device-provisioning-parameters-explained)
- [Interoperability Levels](#interoperability-levels)
- [Example Use Case](#example-use-case)
- [Environment Variables](#environment-variables)
- [Expected Folder Structure](#expected-folder-structure)
- [Troubleshooting](#troubleshooting)
- [References](#references)


## Interoperability Layer

According to IEEE, interoperability is "the ability of two or more systems or components to exchange information and to use the information that has been exchanged". In general terms, there is a list of interoperability layers defined, which includes: interoperability governance, integrated public service governance, legal interoperability, organisational interoperability, technical/syntactic interoperability, and semantic interoperability. 

The following sections describe the FIWARE-based interoperability framework, called Interoperability Layer, which has been used in the context of the DEDALUS project, where semantic interoperability is of outmost importance. Semantic interoperability provides that the precise format and meaning of exchanged data and information is preserved and understood throughout exchanges between parties. It includes developing vocabularies and schemas to describe data exchanges and ensures that data elements are understood in the same way by all communicating parties. This allows various system components to:
- Access shared data through a common vocabulary (e.g., using standard URIs like `https://w3id.org/dco#Temperature`).
- Maintain their local terminology (e.g., `temperature`, `temperatura`, `temperatur`) while remaining interoperable.
  
In the following, we will refer to a generic building, which will be identified as BuildingABC, where a device is installed, which  will be identified as device123, which sends the humidity and co2 measurements to the IoT Agent via the MQTT Broker.


## Architecture Overview

The system leverages a **FIWARE-based architecture** consisting of the following core components:

- **IoT Agent (IoT Agent NGSI-JSON)**: Receives device measurements via MQTT (in JSON) and converts them to NGSI-LD format.
- **Context Broker (Orion-LD)**: Manages context data (entities, attributes, etc.) in NGSI-LD format.
- **Database (MongoDB)**: Stores IoT Agent and Context Broker data.
- **MQTT Broker (Mosquitto)**: Manages message exchange between devices and the IoT Agent.
- **HTTP Web Server (Apache HTTP Server)**: Serves JSON-LD context files for data model semantics.


## MQTT Message Format

Devices publish their sensor data to MQTT topics to enable the IoT Agent to properly process and route the data.

**Topic format:**
```
/json/<api-key>/<device-id>/attrs
```

**Example:**
```
/json/Project-BuildingABC/device123/attrs
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


### MQTT Broker - Mosquitto

The MQTT Broker connects devices and the IoT Agent using MQTT protocol. It can be configured to connect to a public broker or run locally.

- Configuration:
  
```yaml

connection remote_mosquitto
address test.mosquitto.org:1883
topic /json/Project-BuildingABC/# in
```

### IoT Agent - IoT Agent NGSI-JSON

The purpose of the IoT Agent component is to take the measurements sent by the IoT Platform on the MQTT queue and to perform the appropriate transformations in terms of both naming and format to send the information to the Context Broker component. These transformations ensure that the data are standardized and compatible with the internal systems. The naming transformations are performed in compliance with the configurations, which instructs the IoT Agent on how it must translate the external terms (used by device) into the terms internal to the framework used by the Context Broker. These internal terms are contained in the Context File, which represents the common vocabulary agreed upon by all parties involved. This common vocabulary ensures that all data are consistently named and formatted, facilitating seamless interoperability and integration across different systems and platforms. Furthermore, the format used to communicate information to the Context Broker is NGSI-Linked Data (LD), which is a subset of the standard JSON-LD format. NGSI-LD provides a structured and efficient way to represent context information, enabling the Context Broker to process and manage the data effectively. By adhering to these standardized terms and formats, the IoT Agent ensures that the data can be accurately interpreted and utilized by the Context Broker, enabling effective data management and analysis. 


The IoT Agent is exposed on port `4041`. 

- Configuration (key environment variables):
  
```bash

IOTA_CB_HOST=orion                  # Context Broker hostname
IOTA_MQTT_HOST=mosquitto            # MQTT Broker hostname
IOTA_CB_NGSI_VERSION=ld             # Use NGSI-LD format
IOTA_JSON_LD_CONTEXT=http://context/ngsi-project-context.jsonld
IOTA_FALLBACK_TENANT=your_project
IOTA_FALLBACK_PATH=/your_project_path
```

### Context Broker - Orion-LD

The Context Broker acts as central orchestrator of context data (entities, attributes, and relationships) and is responsible for:
•	Storing, updating, and publishing real-time or historic context information
•	Enabling subscription/notification to context changes (e.g., to analytics engines, dashboards, or connectors).

It runs on port `1026`, responsible for storing and updating NGSI-LD entities. 

- Configuration:

```bash
-dbhost mongo-db
-db orionld
-logLevel DEBUG
```

### HTTP Web Server - ???

The Web Server provides access to context files to all components that need them.

It runs on port `3004`. Serves JSON-LD context files that define the semantic data model, enabling clients to understand attribute meanings.

- Configuration:
  
```
http://context/ngsi-project-context.jsonld
```

### Database - MongoDB

It stores all provisioning and context data. 
It runs on port `27017`.


## Provisioning Examples
This section demonstrates how to provision entities, services, and devices in the FIWARE ecosystem.

### Context File (`ngsi-project-context.jsonld`)
Semantic interoperability allows to refer to shared concepts using common identifiers, while still preserving their ability to use local terms internally and independently. For example, the concept of temperature can be globally identified by the URI https://w3id.org/dco#Temperature. One component might refer to it internally as "temperature" (in English), another as "temperatura" (in Italian), and yet another as "temperatur" (in Danish). Despite these variations, all components understand they are referring to the same shared concept, thanks to the common Uniform Resource Identifiers (URI). This level of semantic alignment in the Interoperability Layer leverages on an external Context File. As above described, the Context File serves as a mapping between local terms used by each component and their corresponding universal URIs. These URIs are recognized and accepted across all systems involved in data processing.

In the DEDALUS project context, some terms have been described in the DEDALUS ontology ( https://github.com/engsep/dedalus-ontology/ ).

- Context File example (`ngsi-project-context.jsonld`)
  
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
		"humidity": "https://engsep.github.io/dedalus-ontology/index-en.html#Humidity",
		"co2": "https://engsep.github.io/dedalus-ontology/index-en.html#CO2",
		"temperature": "https://engsep.github.io/dedalus-ontology/index-en.html#Temperature"
  }
}
```

### Building Entity Provisioning
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
  "id": "urn:ngsi-ld:Building:BuildingABC",
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
    "value": "BuildingABC"
  }
}
```

### Device Entity Provisioning
Associate a device to the building entity, enabling its measurements to be linked to a specific asset:

```http
POST http://localhost:1026/ngsi-ld/v1/entities/
Headers:
  fiware-service: your-project
  fiware-servicepath: /your-project-servicepath
  Content-Type: application/json

Payload:
{
  "id": "urn:ngsi-ld:Device:device123",
  "type": "Device",
  "name": {"type": "Property", "value": "device123"},
  "controlledAsset": {
    "type": "Relationship",
    "object": ["urn:ngsi-ld:Building:BuildingABC"]
  }
}
```

### Service Group Provisioning
Register a service group in the IoT Agent, linking API keys to the Context Broker and entity types:
```http
POST http://localhost:4041/iot/services
Headers:
  fiware-service: your-project
  fiware-servicepath: /your-project-servicepath
  Content-Type: application/json
Payload:
{
  "services": [
    {
      "apikey": "Project-BuildingABC",
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
  fiware-service: your-project
  fiware-servicepath: /your-project-servicepath
  Content-Type: application/json
Payload:
{
  "devices": [
    {
      "device_id": "ws32158",
      "entity_name": "urn:ngsi-ld:Device:device123",
      "entity_type": "Device",
      "apikey": "Project-BuildingABC",
      "protocol": "IoTA-JSON",
      "transport": "MQTT",
      "timezone": "Europe/Berlin",
      "explicitAttrs": [
        "temperature", "humidity", "co2", "dateObserved", "unitCode"
      ],
      "attributes": [
        {"object_id": "datetime", "name": "dateObserved", "type": "Property"},
        {"object_id": "temperature", "name": "temperature", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "CEL"}}},
        {"object_id": "humidity", "name": "humidity", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "P1"}}},
        {"object_id": "co2", "name": "co2", "type": "Property",
         "metadata": {"unitCode": {"type": "Text", "value": "KGM"}}},
        
      ]
    }
  ]
}
```
### Summary – Device Provisioning Parameters Explained

| Parameter        | Description |
|------------------|-------------|
| `device_id`      | The unique identifier for the device as seen in the MQTT topic. It is used to match incoming data from the topic `/json/<apikey>/<device_id>/attrs`. |
| `entity_name`    | The NGSI-LD URN for the device entity that will be created in the Context Broker. It should follow the format: `urn:ngsi-ld:<entity_type>:<device_id>`. |
| `entity_type`    | The type of the entity, typically `"Device"`, used by the Context Broker for classification. |
| `apikey`         | A key used to distinguish services and filter MQTT topics. It becomes part of the MQTT topic structure (e.g., `/json/<apikey>/...`). |
| `protocol`       | Specifies the format of the incoming payload. In this case: `"IoTA-JSON"` for plain JSON format. |
| `transport`      | Communication protocol used by the device, typically `"MQTT"` for lightweight IoT messaging. |
| `timezone`       | The timezone used for interpreting timestamps (e.g., `dateObserved`). Helps normalize time-based data across deployments. |
| `explicitAttrs`  | A list of attribute names expected from the device. It is used by the IoT Agent to filter and validate incoming payloads. Attributes not listed here are ignored. |
| `attributes`     | A list that defines how incoming JSON fields (e.g., `"temperature"`, `"datetime"`) are mapped to NGSI-LD properties. Includes: <ul><li>`object_id`: the key in the MQTT payload</li><li>`name`: the NGSI-LD attribute name</li><li>`type`: NGSI-LD type (usually `"Property"`)</li><li>`metadata`: optional unit codes and other metadata</li></ul> |



## Running the System with Docker Compose

The `docker-compose.yml` file provided in this project sets up all required components (Orion-LD, IoT Agent, MongoDB, MQTT Broker, HTTP Server) for a complete semantic IoT integration stack.

>  **Note**:  
> The configuration is currently tailored for the **Dedalus** project and uses:
> - A custom `ngsi-dedalus-context.jsonld` context file located in the `models/` directory
> - Default tenant (`dedalus`) and service path (`/neogrid`) for provisioning
>
> However, it is **fully customizable**. You can easily modify:
> - The context file (e.g., replace with `ngsi-yourproject-context.jsonld`)
> - The `IOTA_FALLBACK_TENANT`, `IOTA_FALLBACK_PATH`, and `IOTA_JSON_LD_CONTEXT` environment variables
> - MQTT topic structure via the `apikey` used during provisioning


Ensure the following components are installed and running:
•	**Docker (Version 23.0.3) & Docker Compose (Version 2.38.2)**

To spin up the full environment, run:

```bash
docker-compose up -d
```
This will:
- Build and start all services in **detached mode** (`-d`)
- Serve your context file from:  
  `http://localhost:3004/ngsi-dedalus-context.jsonld` *(or your custom context)*
- Expose the **IoT Agent** on:  
  `http://localhost:4041`
- Expose the **Orion Context Broker (Orion-LD)** on:  
  `http://localhost:1026`
- Expose the **MQTT Broker** on:  
  `tcp://localhost:1883`

## Verify Running Services

Use the following command to check that all services are up and healthy:

```bash
docker ps
```
You should see all containers (orion-ld, iot-agent, mongo-db, mosquitto, webserver-context) with the status healthy or up


### Environment Variables

The `docker-compose.yml` relies on environment variables defined in the `.env` file. Customize ports, versions, and paths according to your environment.

### Expected Folder Structure
```plaintext
project-root/
├── docker-compose.yml
├── .env
├── models/
│ └── ngsi-project-context.jsonld
├── conf/
│ └── mime.types
├── mosquitto/
│ └── mosquitto.conf
```
Ensure that volume mounts in Docker Compose correspond to these paths.

### Troubleshooting
- **Port conflicts:** Check if ports 1026, 4041, 27017, 1883, 3004 are free.
- **MQTT messages not received:** Verify Mosquitto config and topic subscription.
- **Device provisioning fails:** Double-check API keys and service paths.

### References
- [FIWARE NGSI-LD API](https://fiware.github.io/specifications/ngsild/)
- [MQTT Protocol](https://mqtt.org/)
- [JSON-LD Contexts](https://www.w3.org/TR/json-ld11/)
