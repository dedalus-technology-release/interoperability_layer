# 🔌 DEDALUS – Interoperability Layer (FIWARE-Based Architecture)

This repository contains a modular and extensible **FIWARE-based Interoperability Layer**, built on top of the **NGSI-LD standard**, designed to enable real-time communication and semantic data exchange between heterogeneous IoT systems.

---

## 🧱 Core Components

The main components of this architecture are:

- **🟡 NGSI-LD IoT Agent (JSON over MQTT)**  
  Receives measurements from devices via MQTT (JSON payload), maps them into NGSI-LD format, and forwards them to the Context Broker.

- **🟢 Orion-LD Context Broker**  
  Core component responsible for managing entities, context data, subscriptions, and registrations using NGSI-LD.

- **🗃️ MongoDB**  
  Persistent data storage used by Orion-LD and the IoT Agent.

- **📂 Apache HTTP Server**  
  Lightweight service used to serve JSON-LD context files (`@context`), including domain-specific customizations.

---

## 📂 Repository Structure

```text
.
├── docker-compose.yml            # Main Docker Compose file
├── .env                          # Environment configuration file
├── data-models/                  # Custom JSON-LD context files
│   ├── user-context.jsonld
│   └── ngsi-dedalus-context.jsonld
├── conf/
│   └── mime.types                # Ensures correct MIME for .jsonld
├── scripts/                      # Custom data acquisition and mapping 
│   └── ...                       # DO NOT COMMIT sensitive data
├── script/
│   └── Pilot/            # Provisioning and registration logic
└── README.md
```

## 🔧 JSON-LD Context Customization

Custom JSON-LD context files should be placed in:

```plaintext
./data-models/
```

These are served from the `ld-context` service and referenced in payloads via URLs such as:

```json
"@context": [
  "http://context/user-context.jsonld",
  "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.8.jsonld"
]
```

## 🧩 Customization (Data Gathering)

Custom logic for acquiring, transforming, or mapping pilot-specific data sources is placed in:
```plaintext
./scripts/
```


This directory contains scripts and Dockerfiles for:

- Connecting to external APIs or data sources (e.g., climate sensors, building systems)
- Parsing and normalizing raw data
- Creating NGSI-LD-compliant entities for injection into Orion-LD

> ⚠️ This folder may contain sensitive data or credentials. Do **not** commit personal information. Use `.env` files or secrets management when necessary.

Each service can be run as a standalone microservice, already integrated into the `docker-compose.yml`.

## 🛠️ Entity Provisioning (Customization)

The **provisioning** phase involves registering devices, their metadata, and relationships within the Context Broker so that the platform can correctly recognize and manage them.

### Where is the provisioning located?

Provisioning scripts are located in the folder:


```plaintext
./script/Pilot/
```

This folder includes example provisioning scripts based on the **Dedalus** pilot. These examples cover:

- Startup scripts for registering device metadata
- Mapping of device IDs, MQTT topics, and NGSI-LD attributes
- Optional test data injection

You can customize these scripts for your pilot needs and extend them to include subscriptions, relationships, and default data values.

Provisioning is automatically triggered when the stack is up and the IoT Agent is healthy.

## 🛠️ Provisioning Scripts: Organization and Execution

### Script Organization

Provisioning scripts are organized into numbered folders representing different provisioning phases or tasks, for example:

- `100 - CB - Create Entity`
- `200 - IOT - Create Service Group`
- `300 - IOT - Create Provisioned Device`

Each folder contains multiple script files named with numeric prefixes (e.g., In our case `101 - CB - Create Entity Building.txt`, `102 - CB - Create Entity Building.txt`) to indicate execution order.

### Automation Script

A Python helper script (`read_script.py`) is used to automate the execution of these provisioning scripts. It:

- Reads all script files in the specified folders.
- Sorts them by their numeric prefixes to ensure the correct execution order.
- Executes only scripts containing `curl` commands, skipping others.
- Prints output and errors of each command for easier debugging.

### 🛠️ Automated Provisioning via Docker Compose

The provisioning process is fully automated and runs inside a dedicated Docker container managed by `docker-compose.yml`.

- The `provisioning` service is built from `script/Pilot/Dockerfile`.
- It depends on the `iot-agent` service and starts only after `iot-agent` passes its health check.
- This container runs the Python helper script described above, executing all provisioning commands in order.
- Provisioning logs can be inspected via `docker logs provisioning`.

### Benefits

- **Automatic execution:** provisioning runs without manual intervention.
- **Ordered provisioning:** numeric prefixes enforce execution order.
- **Isolated environment:** provisioning runs in a dedicated container separate from main services.

### How to run 
Run containers with one of these commands:
- `$ docker compose up -d` or, e.g.,
- `$ PORT=8080 docker compose up -d` (to run the demo, e.g., from http://localhost:8080)

Stop containers with one of these commands:
- `$ docker compose down` or
- `$ docker rm -f $(docker ps -aq)` (⚠️ removes ALL Docker containers!)
