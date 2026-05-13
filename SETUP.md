# Setup

Solaris_Ai is a pure-Python conceptual AI system. Setup takes a
couple of minutes. There are no third-party dependencies.

---

## Requirements

- **Python 3.11 or later.** Check with `python3 --version`.
- A terminal (Terminal.app on macOS, any shell on Linux, PowerShell
  or Windows Terminal on Windows).
- Optional but recommended: `git` to clone the repository.

That is the entire requirement list. The runtime, the CLI demo and
the web UI are all stdlib-only.

---

## 1. Get the code

Either clone the repo:

```sh
git clone https://github.com/fopearcano/solaris-ai.git
cd solaris-ai
```

…or download the zip from GitHub and `cd` into the unpacked folder.

You should be in the folder that contains `pyproject.toml`, `src/`,
and `README.md`. **Run every command below from this folder** — the
project root, not from inside `src/solaris/`.

You can confirm with:

```sh
ls pyproject.toml src README.md
```

---

## 2. (Recommended) Create a virtual environment

A venv keeps Solaris's two console scripts (`solaris`, `solaris-web`)
isolated from your system Python.

macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Once active, every `python` / `pip` command uses the venv. Run
`deactivate` to leave it.

If you skip this step, you can still install — `pip install --user`
or add `--break-system-packages` may be needed depending on your
distro.

---

## 3. Install

```sh
pip install -e .
```

(Use `pip3` instead of `pip` on macOS / any system where `pip` is
not on the path.)

This:

- Installs the `solaris` package in **editable mode** — changes to
  source files take effect immediately, no reinstall needed.
- Adds two console scripts:
  - `solaris` — the CLI demo.
  - `solaris-web` — the interactive web UI.

Verify:

```sh
which solaris solaris-web   # macOS / Linux
where solaris solaris-web   # Windows
```

---

## 4. Run

### CLI demo

```sh
solaris
```

You will see, in order:

1. The bus subscriptions printed — every module's listeners.
2. AION emitting an absence-Stimulus ('I exist!') after silence.
3. External Stimuli flowing through Cognition → I/O → Action.
4. A Reaction triggering Backpropagation → Auto-Regeneration,
   which rewrites I/O Module's `action_threshold` at runtime.
5. The final Inner MAP snapshot and a clean death.

Total runtime: about 3 seconds.

### Web UI

```sh
solaris-web
```

Open <http://127.0.0.1:8765/> in your browser.

Stop the server with Ctrl+C in the terminal, or click **Die** in
the UI.

To use a different port:

```sh
solaris-web --port 8800
```

To bind on all interfaces (e.g. for a remote browser):

```sh
solaris-web --host 0.0.0.0 --port 8765
```

---

## Running without installing

If you'd rather not run `pip install`:

```sh
PYTHONPATH=src python3 -m solaris        # CLI demo
PYTHONPATH=src python3 -m solaris.web    # web UI
```

These work from the project root only. The `PYTHONPATH=src` part
tells Python to look inside `src/` for the `solaris` package.

---

## Platform notes

### macOS

- The python.org installer ships only `python3` / `pip3` (there is
  no `python` / `pip` by default). Use the `3`-suffixed forms.
- Homebrew Python is the same. Pyenv users can shim either name.
- If `pip3 install -e .` complains about an "externally managed
  environment", create a venv (Step 2) — that is the right fix.

### Linux

- Most distros ship `python3`. Some need `python3-venv` from the
  package manager (`sudo apt install python3-venv` on Debian /
  Ubuntu).
- `python` is sometimes a 2.x alias, sometimes missing. Use
  `python3` to be safe.

### Windows

- The Python launcher is the most reliable invocation:
  `py -3 -m solaris`, `py -3 -m solaris.web`.
- After `pip install -e .` inside an activated venv, `solaris`
  and `solaris-web` work from any directory.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'solaris'`

One of:

- You are not at the project root. `cd` to the folder that contains
  `pyproject.toml`.
- You are not using `PYTHONPATH=src`, **and** you have not run
  `pip install -e .`. Pick one.
- You tried `python3 src/solaris/conscience.py` directly. That will
  not work — the imports are absolute. Use `solaris`,
  `python3 -m solaris`, or `python3 -m solaris.web` instead.

### `zsh: command not found: python` (macOS)

Use `python3`. Likewise `pip` → `pip3`.

### `command not found: solaris` / `solaris-web`

Either:

- You have not run `pip install -e .` yet.
- Your virtualenv is not active (`source .venv/bin/activate`).
- The script directory is not on your `PATH`. Check with
  `which solaris` (macOS / Linux) or `where solaris` (Windows). On
  some Linux distros, `pip install --user` puts scripts in
  `~/.local/bin`, which may not be on `PATH` by default.

### `OSError: [Errno 48] Address already in use`

Port 8765 is taken — either an old `solaris-web` is still running,
or another program owns the port. Kill the previous server, wait a
moment, or pick a different port:

```sh
solaris-web --port 8800
```

### The browser shows "connecting…" forever

The page loaded but the SSE stream did not open. Likely causes:

- A browser extension or proxy interfering with localhost.
- Loading the page from a different origin than the server is
  serving (the server is `http://127.0.0.1:8765/` by default; do
  not load via `file://`).

### `pip install -e .` fails with "no setup.py found"

You are not at the project root, or your `pip` is too old. Update:
`pip install --upgrade pip`.

---

## Updating

If you cloned with `git`:

```sh
git pull
pip install -e .   # only if pyproject.toml changed
```

If you downloaded a zip, re-download and unpack.

---

## Uninstall

```sh
pip uninstall solaris
```

If you used a venv, you can also just delete the `.venv` folder.
Deleting the project folder removes everything else.
