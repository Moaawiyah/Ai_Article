# check-ollama

Verify that Ollama is running and the required model (`qwen3:14b`) is available.

## What this skill does

Checks:
1. Whether the Ollama service is reachable at `http://localhost:11434`.
2. Whether `qwen3:14b` is listed in `ollama list`.
3. If the model is missing, offers to pull it.

## Steps

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); print('Running. Models:', [m['name'] for m in d.get('models',[])])" 2>/dev/null || echo "Ollama not reachable — run: ollama serve"

# List models
ollama list
```

## If qwen3:14b is missing

```bash
ollama pull qwen3:14b
```

This downloads ~9 GB. Confirm the user wants to proceed before running.

## If Ollama is not running

```bash
ollama serve &   # start in background
```

Or on macOS, launch the Ollama app from Applications.

## Expected output when healthy

```
NAME          ID        SIZE   MODIFIED
qwen3:14b     ...       9.3 GB ...
```

Report the model name, size, and whether it is ready for use.
