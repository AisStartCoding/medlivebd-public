"""Demonstration picker routes (port of `routes/demo.routes.ts`; CLAUDE.md §4.1).

With `DEMO_MODE` off these refuse, and the console shows the login screen.
"""

from medlive.modules.demo import views as demo
from medlive.core.router import Router
from medlive.core.validation import validate
from medlive.domain.schemas import booking as s

routes = Router()

routes.get("/demo/status", demo.status)
routes.get("/demo/consoles", demo.list_consoles)
routes.post("/demo/token", validate(body=s.demo_token_body), demo.mint_token)
