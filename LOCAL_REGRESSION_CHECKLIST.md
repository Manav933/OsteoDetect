# Local regression checklist (Osteoporosis platform)

**Environment:** ML `http://127.0.0.1:8000`, Django `http://127.0.0.1:8080` (e.g. `run_servers.bat`).  
**How to use:** Tick boxes as you go. For two-user cases, use normal window + incognito (or two browsers).

---

## Smoke & auth

- [ ] **L-01** — Open `http://127.0.0.1:8080` → app loads (login or dashboard).
- [ ] **L-02** — Register **Doctor** → lands on doctor dashboard (no error).
- [ ] **L-03** — Register **Patient** (minimal fields) → patient dashboard (no error).
- [ ] **L-04** — **Logout** → cannot reach protected pages without logging in again.

## Diagnosis & ML

- [ ] **L-05** — **Doctor**, ML **running**, valid image &lt; 5MB → result **COMPLETED** with class / confidence / risk.
- [ ] **L-06** — **Patient**, ML **running**, same happy path → **COMPLETED**.
- [ ] **L-07** — ML **stopped** (or broken URL) → diagnosis saved as **FAILED**, user sees error (no 500).
- [ ] **L-08** — Upload **&gt; 5MB** or bad extension → form error, no false **COMPLETED**.

## Access control & history

- [ ] **L-09** — Patient **A** opens `/diagnose/&lt;B’s UUID&gt;/` → **403** / permission denied.
- [ ] **L-10** — Patient opens **own** diagnosis UUID → **200**, report visible.
- [ ] **L-11** — Patient with 2+ scored diagnoses → `/patient/&lt;own UUID&gt;/history/` loads, trend OK.

## Delete

- [ ] **L-12** — Patient **delete own** diagnosis → removed from list.
- [ ] **L-13** — Patient cannot delete **another** patient’s record → **403** or no effect.

## ML & config

- [ ] **L-14** — `GET http://127.0.0.1:8000/health` → JSON healthy; `model_loaded` true when model files present.
- [ ] **L-15** — If you change ML port in `.env`, confirm Django calls the correct service (known issue: duplicate `ML_SERVICE_URL` in `settings.py` may override).

## Optional

- [ ] **L-16** — User with role **ADMIN** → login works; note which dashboard appears.

---

## Quick notes

| Need | Action |
|------|--------|
| Fresh DB | Remove `backend/db.sqlite3`, migrate, re-register users |
| UUIDs | Copy from dashboard “View” links |
| Automated smoke | From repo root: `cd e2e` then run pytest with **backend venv** Python (see below) |

### Automated smoke (pytest)

PowerShell (paths are examples—adjust if your folder differs):

```powershell
cd "...\osteoporosis_platform\backend"
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pip install -r ..\e2e\requirements.txt
cd ..\e2e
..\backend\venv\Scripts\python.exe -m pytest -q
```

Expect **1 passed**, **14 skipped** (Playwright stubs). A warning about missing `staticfiles` is normal until you run `collectstatic`.

To implement browser tests: `..\backend\venv\Scripts\python.exe -m playwright install`, then remove `@pytest.mark.skip` from a stub and fill in selectors.
