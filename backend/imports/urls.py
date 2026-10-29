"""`/hospital/imports`, a hospital's own data set by set (port of `routes/import.routes.ts`;
BACKEND.md §7.7, PRD.md §14b, S-B-14).

Checking writes only the batch; committing, undoing and discarding each
take an idempotency key and are audited (FR-IMP-08). The file routes parse
their own bounded body: JSON may escape each CSV byte as six, so the
envelope is bounded at six times five MiB, and the schema holds the CSV
itself to five MiB of UTF-8 (FR-IMP-09). `analyse` writes nothing, so it
carries no key.
"""

from backend.imports import views as imports
from backend.core.security.auth import WRITE
from backend.core.security.auth import require_auth
from backend.core.security.auth import require_role
from backend.core.http.router import Router
from backend.core.validation.requests import validate
from backend.domain.schemas import imports as s
from backend.domain.schemas.settings import empty_body

routes = Router()

_admin = (require_auth, require_role("hospital_admin"))

#: `json({ limit: MAX_IMPORT_BYTES * 6 + 64 * 1024 })`, after `...admin`
#: (`parse_after=2`): an unauthenticated body is refused before it is read.
FILE_BODY_LIMIT = s.MAX_IMPORT_BYTES * 6 + 64 * 1024

routes.get("/hospital/imports/templates/:set", *_admin, validate(params=s.import_set_params), imports.get_template)
routes.get("/hospital/imports", *_admin, imports.list_batches)
routes.get("/hospital/imports/:id", *_admin, validate(params=s.import_params), imports.get_one)
routes.post(
    "/hospital/imports",
    *_admin,
    WRITE,
    validate(body=s.import_upload_body),
    imports.check,
    body_limit=FILE_BODY_LIMIT,
    parse_after=2,
)
routes.post(
    "/hospital/imports/analyse",
    *_admin,
    validate(body=s.import_analyse_body),
    imports.analyse,
    body_limit=FILE_BODY_LIMIT,
    parse_after=2,
)
routes.post(
    "/hospital/imports/mapped",
    *_admin,
    WRITE,
    validate(body=s.import_mapped_body),
    imports.check_mapped,
    body_limit=FILE_BODY_LIMIT,
    parse_after=2,
)
for _path, _handler in (("commit", imports.commit), ("undo", imports.undo), ("discard", imports.discard)):
    routes.post(
        f"/hospital/imports/:id/{_path}",
        *_admin,
        WRITE,
        validate(params=s.import_params, body=empty_body),
        _handler,
    )
