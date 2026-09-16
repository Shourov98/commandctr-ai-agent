# CommandCtr AI Agent

FastAPI service for the CommandCtr AI/product automation agent.

## Setup

```powershell
cd D:\RAJUAN-PERSONAL\VSCODE\commandctr\commandctr-ai-agent
uv sync
```

Create or copy the required `.env` values before running the service.

## Run

Run on the default Uvicorn port `8000`:

```powershell
uv run python -m uvicorn app.main:app --reload --reload-dir app
```

Run on a separate agent port, for example `9100`:

```powershell
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 9100 --reload --reload-dir app
```

Open:

```text
http://localhost:9100
```

## Test

```powershell
uv run python -m pytest
```
