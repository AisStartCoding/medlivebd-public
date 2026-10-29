"""Demonstration picker routes (port of `routes/demo.routes.ts`; CLAUDE.md §4.1).

With `DEMO_MODE` off these refuse, and the console shows the login screen.
"""

from backend.demo import views as demo
from backend.core.http.router import Router
from backend.core.validation.requests import validate
from backend.domain.schemas import booking as s

routes = Router()

routes.get("/demo/status", demo.status)
routes.get("/demo/consoles", demo.list_consoles)
routes.post("/demo/token", validate(body=s.demo_token_body), demo.mint_token)
