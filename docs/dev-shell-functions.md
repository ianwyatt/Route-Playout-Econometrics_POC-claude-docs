# Dev shell functions

Convenience helpers for the local dev loop. Add to `~/.zshrc` (these are
not committed to the repo because they hard-code your local project
path).

The Streamlit helpers (`startstream` / `stopstream`) already exist; the
FastAPI ones below are new with Plan B.

```zsh
# Streamlit (existing — DuckDB-backed read-only query interface)
startstream() {
    cd /home/dev/projects/Route-Playout-Econometrics_POC || return
    case "$1" in
        demo)   DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504 ;;
        global) DEMO_MODE=true DEMO_PROTECT_MEDIA_OWNER="Global" streamlit run src/ui/app.py --server.port 8504 ;;
        *)      streamlit run src/ui/app.py --server.port 8504 ;;
    esac
}

stopstream() {
    pkill -f "streamlit run" || true
}

# FastAPI (Plan B — JSON layer for the React frontend)
startapi() {
    cd /home/dev/projects/Route-Playout-Econometrics_POC || return
    uv run uvicorn src.api.main:app --reload --port "${API_PORT:-8000}"
}

stopapi() {
    pkill -f "uvicorn src.api.main" || true
}
```

Both can run side by side — Streamlit on `:8504`, FastAPI on `:8000` —
attaching to the same DuckDB file (read-only, multiple readers
allowed).

## Why shell functions, not Claude Code background processes

Running long-lived dev servers via Claude Code's `run_in_background`
exhausts the conversation token budget — every line of uvicorn or
Streamlit output streams back to the model. Always use these helpers
from your terminal instead.
