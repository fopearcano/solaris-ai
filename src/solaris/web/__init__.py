"""Web UI for Solaris_Ai.

A small asyncio HTTP + Server-Sent-Events server that streams every
Bus signal to a browser, plus a single-page SVG visualisation that
renders the module graph and pulses edges as signals fire.

Run:

    PYTHONPATH=src python -m solaris.web

Then open http://127.0.0.1:8765/.

This module deliberately avoids any third-party dependency — the
server is implemented on top of asyncio.start_server and the
frontend is plain HTML / CSS / vanilla JS.
"""
