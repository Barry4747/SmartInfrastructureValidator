# Smart Infrastructure Validator 📡

A comprehensive, localized 5G/4G network telemetry aggregator and simulation testing tool. Built to validate and visualize complex telecommunication node metrics in real-time.

![System Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Tech Stack](https://img.shields.io/badge/Tech-FastAPI%20%7C%20PostgreSQL%20%7C%20Docker-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-success)

## 🌟 Features

- **Real-Time Telemetry Aggregation**: Centralized FastAPI aggregator receiving live metrics (CPU temp, active users, throughput) from distributed BTS nodes.
- **WebSocket Streaming**: Live push notifications for active alarms and real-time dashboard updates.
- **Node Simulators**: Configurable 4G (eNodeB) and 5G (gNodeB) simulated nodes using dynamic background loops for producing realistic telemetry data.
- **Fault Injection Framework**: Dedicated API endpoints on simulators to trigger specific faults (e.g., cooling system failure, traffic spikes) and test the entire infrastructure's resilience.
- **Interactive UI**: Minimalist, glassmorphism-styled frontend built with Vanilla JS and Leaflet.js showcasing geospatial node data and active alarms.
- **PostGIS Integration**: Storage and retrieval of geospatial metrics.

## 🚀 Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL with PostGIS extensions (via TimescaleDB image)
- **Frontend**: HTML5, Vanilla CSS, JS (Leaflet.js for maps)
- **Infrastructure**: Docker, Docker Compose

## 🛠️ Quick Start

The entire project is containerized using Docker Compose. Ensure you have Docker installed and running on your system.

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd SmartInfrastructureValidator
   ```

2. **Start the network:**
   ```bash
   docker compose up -d --build
   ```

3. **Access the Dashboard:**
   Open your browser and navigate to: `http://localhost:8000/`

## 🧪 Fault Injection

You can test the system's response to failures by injecting faults directly from the frontend UI or via API calls.

*   **Cooling Failure:** Triggers a rapid increase in CPU temperature.
    *   **Frontend**: Click "Inject Fault" in the node's map popup.
    *   **API**: `POST http://localhost:<FAULT_PORT>/api/fault/cooling`

*   **Resolve Issue:** Restores node parameters to normal.
    *   **Frontend**: Click "Fix Node" in the node's map popup.
    *   **API**: `POST http://localhost:<FAULT_PORT>/api/fault/fix`

## 📁 Project Structure

```text
├── aggregator/          # Centralized metric collection & UI
│   ├── crud/            # Database operations
│   ├── routers/         # REST API and WebSocket routes
│   ├── static/          # Frontend assets (HTML, CSS, JS)
│   └── main.py          # Entry point
├── bts_simulator/       # Dummy 4G/5G nodes generating traffic
│   ├── client.py        # HTTP client for aggregator registration
│   ├── state.py         # Logic for node health decay/recovery
│   └── main.py          # Background telemetry engine
├── README.md
├── docker-compose.yml   # Infrastructure definitions
└── .gitignore
```

## 📄 License
This project is for demonstration and portfolio purposes. Feel free to explore or branch!