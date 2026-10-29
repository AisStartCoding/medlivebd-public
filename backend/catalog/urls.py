"""Public discovery routes (port of `routes/discovery.routes.ts`): the unauthenticated surface."""

from backend.catalog import views as discovery
from backend.core.http.router import Router
from backend.core.validation.requests import validate
from backend.domain.schemas import booking as s

routes = Router()

routes.get("/config", validate(query=s.config_query), discovery.get_config)
routes.get("/search", discovery.search)
routes.get("/hospitals", discovery.list_hospitals)
routes.get("/hospitals/:id", validate(params=s.id_params), discovery.get_hospital)
routes.get("/hospitals/:id/logo", validate(params=s.id_params), discovery.get_logo)
routes.get("/hospitals/:id/doctors", validate(params=s.id_params), discovery.get_hospital_doctors)
routes.get("/doctors", discovery.list_doctors)
routes.get("/doctors/:id", validate(params=s.id_params), discovery.get_doctor)
routes.get("/sessions", discovery.list_sessions)
routes.get("/sessions/:id/availability", validate(params=s.id_params), discovery.get_availability)
