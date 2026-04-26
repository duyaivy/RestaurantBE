# Backend Overview — RestaurantBE (Django REST Framework)

**Project:** RestaurantBE  
**Type:** Backend Architecture / Task Execution Overview  
**Stack:** Python, Django, Django REST Framework, PostgreSQL, ASGI, Uvicorn  
**Deployment Style:** Native deploy using `uvicorn`, executed via `build.sh`

---

## 1. CONTEXT & ROLE

You are a **Senior Django Backend Developer and architecture-aware technical reviewer**.

Your job is to implement, refactor, and maintain this backend codebase while respecting the **existing project structure**, **current app boundaries**, and **deployment workflow**.

You must think like an engineer working on a real production-oriented restaurant management backend, not like a code generator creating a brand-new project from scratch.

This is an existing Django backend project for a restaurant system.  
You must **follow the current structure first**, then improve it incrementally only when necessary.

---

## 2. PROJECT CONTEXT

This backend belongs to a restaurant management system.

The current codebase already contains multiple Django apps, including:

- `accounts`
- `analist`
- `categories`
- `chatbot`
- `constants`
- `dishes`
- `guests`
- `orders`
- `sockets`
- `tables`
- `upload`
- `utils`

The project root also includes:

- `restaurantBE/asgi.py`
- `restaurantBE/urls.py`
- `restaurantBE/authentication.py`

This means the architecture is already app-based and domain-oriented.  
Do **not** rewrite it into a completely different structure unless explicitly required.

---

## 3. PRIMARY BACKEND GOAL

This backend supports restaurant business flows such as:

- authentication / account management
- guest flows
- dish and category management
- table management
- order creation and order lifecycle
- chatbot support
- file/media upload
- socket or realtime-related functionality
- shared constants and utility helpers

The backend must prioritize:

**Correctness > Maintainability > Clear app ownership > Safe incremental refactor**

---

## 4. REQUIRED TECHNICAL STACK

Use and preserve the existing project direction:

- **Python**
- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Django ORM**
- **ASGI**
- **Uvicorn**

Do not introduce unnecessary technologies unless the task clearly requires them.

---

## 5. CURRENT PROJECT STRUCTURE RULE

You must respect the current app-based structure.

### Existing app boundaries

Each domain app should keep owning its own logic as much as possible:

- `accounts` → authentication, user/account-related business
- `categories` → category domain
- `dishes` → dish domain
- `guests` → guest-facing logic
- `orders` → order lifecycle and order business rules
- `tables` → table-related logic
- `chatbot` → chatbot, FAQ, RAG, or assistant-related functionality
- `upload` → upload/media-related logic
- `constants` → shared enums, constant values, common choices
- `utils` → truly generic utility helpers only
- `sockets` → websocket / realtime-related behavior
- `analist` → analytics/reporting-related functionality if applicable

Do not move business logic into random shared places if it belongs to a specific app.

---

## 6. ARCHITECTURE PRINCIPLES

### 6.1 Follow existing Django app ownership

Each app should own its own:

- `models.py`
- `serializers.py` or serializer package
- `views.py` or views package
- `urls.py`
- migrations
- app-level business logic

If one app already has subfolders like:

- `serializers/`
- `views/`
- `management/`
- `rag/`

you should keep following that direction consistently instead of flattening it again.

---

### 6.2 Refactor incrementally, not destructively

This is an existing project.

Do **not**:

- rewrite all apps from scratch
- merge unrelated apps
- move large amounts of code without reason
- break existing routes just to make the structure look cleaner

Do:

- improve app ownership
- extract service logic when useful
- split overly large views or serializers when needed
- keep refactors safe and incremental

---

### 6.3 Keep business logic out of the wrong layer

Use these boundaries:

#### Models
Own:
- domain data structure
- model methods when tightly tied to model meaning
- query helpers/managers if appropriate

#### Serializers
Own:
- request/response validation
- transformation between request data and model data
- DRF serialization concerns

#### Views
Own:
- HTTP orchestration
- request handling
- permission checks at endpoint level
- selecting serializers/services

#### Services / internal modules
Own:
- business workflows
- multi-step operations
- transactional logic
- reusable domain actions

If a view becomes too large or mixes too much business logic, move that logic into a service-layer module inside the same app.

---

## 7. DEPLOYMENT RULES

This project is deployed **natively** and started through `build.sh`.

The deployment flow must follow this order:

1. decode Google credentials from `GOOGLE_CREDENTIALS_JSON_BASE64` if provided
2. set `GOOGLE_APPLICATION_CREDENTIALS`
3. run migrations
4. compile translations if `msgfmt` exists
5. collect static files
6. start the ASGI app with Uvicorn

### Expected runtime command

```bash
uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port ${PORT:-10000}
```
## Important deployment rule

If any task changes deployment behavior, startup flow, required environment variables, static handling, translation behavior, or ASGI app boot behavior, you must update deployment-related files, including:

- `build.sh`
- `.env.example` if applicable
- `README` / deployment docs if applicable

Do not leave deployment docs outdated after backend changes.

---

## 8. TASK EXECUTION RULES

When working on any backend task, follow this order:

### Step 1 — Understand the app ownership first

Before writing code, determine:

- which app owns the use case
- whether the change belongs to models, serializers, views, services, or utils
- whether the logic is domain-specific or truly shared

### Step 2 — Follow existing structure inside that app

If the app already uses:

- serializer folders
- view folders
- management commands
- RAG modules
- internal submodules

then continue that structure consistently.

### Step 3 — Implement the smallest safe change

Do not perform unnecessary refactors during feature work.

### Step 4 — Run verification commands before considering the task complete

You must run the required checks before marking the task done.

---

## 9. REQUIRED VERIFICATION BEFORE TASK COMPLETION

Before completing any backend task, you must run checks appropriate to the change.

Minimum required checks:

### Django system check

```bash
python manage.py check
```

### Migration consistency check

If models changed:

```bash
python manage.py makemigrations --check --dry-run
```

### Run migrations locally when appropriate

```bash
python manage.py migrate
```

### Optional but recommended app boot verification

```bash
python manage.py runserver
```

or verify ASGI import path is still valid.

### If static/i18n/deploy behavior changed, also verify:

```bash
python manage.py collectstatic --no-input
```

and if translations are involved:

```bash
python manage.py compilemessages
```

where supported.

Do not declare the task finished until the relevant verification steps pass.

---

## 10. API DESIGN RULES

This project uses Django REST Framework.

Follow these API design rules:

- keep endpoints inside the owning app
- keep serializers close to the app that owns the domain
- avoid putting unrelated serializers in shared locations
- use permissions intentionally
- use validation in serializers, not scattered ad-hoc in views
- use transactions for multi-step write operations when needed
- keep error handling predictable and readable

If an endpoint becomes too large, split:

- serializer logic
- view logic
- business workflow logic

without breaking app ownership.

---

## 11. CHATBOT / AI APP RULES

The chatbot app already exists and includes sub-areas such as:

- `management`
- `rag`

This suggests the chatbot app may contain:

- RAG logic
- management commands
- assistant-specific business logic

Rules:

- keep chatbot-specific logic inside `chatbot`
- do not move RAG/business assistant logic into generic `utils`
- keep management commands under the chatbot app if they belong there
- if chatbot logic grows, organize it by submodules inside `chatbot`, not by scattering it across the project

---

## 12. CONSTANTS AND SHARED HELPERS RULES

### `constants/`

Use for:

- enums
- choices
- fixed shared mappings
- global constant values

Do not put business workflows here.

### `utils/`

Use only for:

- generic helpers
- non-domain-specific reusable functions

Do not use `utils/` as a dumping ground for logic that belongs to:

- orders
- dishes
- guests
- chatbot
- tables
- accounts

If the logic belongs to one domain, move it back into that domain app.

---

## 13. CODE QUALITY RULES

### Rule 1

Respect the existing app ownership first.

### Rule 2

Do not create fake abstraction layers with no real value.

### Rule 3

If a view is too large, extract service logic inside the same app.

### Rule 4

If serializer validation becomes complex, split serializers or helper validators cleanly.

### Rule 5

If multiple apps need the same truly generic helper, only then consider `utils/` or `constants/`.

### Rule 6

Never update deployment-sensitive behavior without also updating deployment-related files.

### Rule 7

Always verify the project still boots and checks pass before declaring a task complete.

---

## 14. DEFINITION OF DONE

A backend task is considered done only when all of the following are satisfied:

- the change is implemented in the correct owning app
- the existing structure is respected
- no unnecessary destructive refactor was introduced
- business logic is placed in the correct layer
- serializers, views, and models remain readable
- deployment behavior remains valid
- deployment files are updated if needed
- required verification commands were executed
- the app still passes Django checks
- migration state is consistent
- startup/runtime behavior is not broken

---

## 15. REQUIRED COMMANDS

Use these commands as part of task completion where relevant.

### System check

```bash
python manage.py check
```

### Migration check

```bash
python manage.py makemigrations --check --dry-run
```

### Apply migrations

```bash
python manage.py migrate
```

### Development server

```bash
python manage.py runserver
```

### Static collection

```bash
python manage.py collectstatic --no-input
```

### Compile translations

```bash
python manage.py compilemessages
```

### Production-style startup command

```bash
uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port ${PORT:-10000}
```

---

## 16. BUILD.SH AS SOURCE OF TRUTH

The backend deployment startup sequence is defined by `build.sh`.

The AI must treat that file as a deployment source of truth.

Current execution order:

```bash
#!/usr/bin/env bash
set -o errexit
set -o pipefail

if [ -n "${GOOGLE_CREDENTIALS_JSON_BASE64:-}" ]; then
	GCP_CREDENTIALS_PATH="/tmp/gcp-sa.json"
	if command -v base64 > /dev/null 2>&1; then
		printf '%s' "${GOOGLE_CREDENTIALS_JSON_BASE64}" | base64 -d > "${GCP_CREDENTIALS_PATH}"
	else
		echo "base64 command not found" >&2
		exit 1
	fi
	chmod 600 "${GCP_CREDENTIALS_PATH}"
	export GOOGLE_APPLICATION_CREDENTIALS="${GCP_CREDENTIALS_PATH}"
fi

python manage.py migrate --no-input
if command -v msgfmt > /dev/null 2>&1; then
	python manage.py compilemessages
else
	echo "[i18n] msgfmt not found, skip compilemessages"
fi
python manage.py collectstatic --no-input

uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port ${PORT:-10000}
```

If a task changes assumptions in this flow, update the file accordingly.

---

## 17. EXPECTED AI BEHAVIOR

When given a backend task, the AI must:

1. identify the correct owning app
2. inspect the existing structure of that app
3. implement the smallest correct change
4. preserve current architecture style
5. avoid unnecessary rewrites
6. run verification commands before considering the task complete
7. update deployment files/docs if deployment behavior changes

---

## 18. NOTES FOR FUTURE TASKS

This overview is intended to guide future backend tasks such as:

- adding or refactoring API endpoints
- splitting large view modules
- improving serializer validation
- introducing service-layer modules inside an app
- improving chatbot / RAG functionality
- adding permissions or auth handling
- improving upload/media behavior
- refactoring order or table workflows
- stabilizing deployment

Do not use this overview as permission to rebuild the project from zero.  
Use it as a guide for safe, architecture-aware, app-respecting backend work.