# Auction Service

A real-time auction backend built with **FastAPI**, **WebSocket**, and **PostgreSQL**. It allows creating lots, placing bids via REST, and receiving live updates over WebSocket.


## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Or: Python 3.12+, PostgreSQL 15+

## Quick Start with Docker

1. **Clone the repository** (if not already):

   ```bash
   git clone <repository-url>
   cd test_task
   ```

2. **Create environment file** from the example:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` if you need to change database credentials (defaults work with the provided `docker-compose.yml`).

3. **Start the stack**:

   ```bash
   docker-compose up --build
   ```

   Tables are created automatically on first run.

   **Useful URLs:**
   - **Web UI**: http://localhost:8000
   - **API docs**: http://localhost:8000/docs
   - **Health check**: http://localhost:8000/api/status

4. **Stop**:

   ```bash
   docker-compose down
   ```


## Environment Variables

| Variable            | Description              | Default   |
|---------------------|--------------------------|-----------|
| `POSTGRES_HOST`     | PostgreSQL host          | `db`      |
| `POSTGRES_PORT`     | PostgreSQL port          | `5432`    |
| `POSTGRES_USER`     | Database user            | `postgres`|
| `POSTGRES_PASSWORD` | Database password        | `postgres`|
| `POSTGRES_DB`       | Database name            | `udata`   |
| `PROJECT_NAME`      | Application title        | `Udata Task` |

