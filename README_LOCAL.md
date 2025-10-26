# FitTwin local stub

Start API:
  uvicorn src.server.main:app --reload

Endpoints:
  GET /measurements/
  GET /dmaas/latest

Replace stub logic with vendor mapping and Supabase once wired.

Quick local verify (use project venv):

1) Activate venv

```bash
cd ~/fitwin-crewai
source .venv/bin/activate
```

2) Run tests (offline, uses TestClient)

```bash
python -m pytest -q
```

3) Optional: run the server and smoke endpoints (new terminal)

```bash
uvicorn src.server.main:app --reload
# then in another terminal:
curl -s http://127.0.0.1:8000/measurements/ | python -m json.tool
curl -s http://127.0.0.1:8000/dmaas/latest | python -m json.tool
```

4) Safe test env file (already created): `.env.test` contains VENDOR_MODE=stub and PORT=8001

# How to Pause and Resume FitTwin Development in VS Code

### 🧭 When You Want to Take a Break
1. Stop the server

In the VS Code terminal where Uvicorn is running, press Ctrl + C.
You should see the message:

Application shutdown complete.

2. Deactivate your virtual environment

Type:

```bash
deactivate
```

This removes the `(.venv)` prefix from your terminal prompt.

3. Close VS Code

- Go to File → Close Workspace or just quit VS Code.
Your environment, Git repo, and all files are saved.

That’s all — everything is preserved exactly as you left it.

---

### 💻 When You’re Ready to Resume Work
1. Reopen your project folder

Open VS Code and open the `fitwin-crewai` folder.

2. Activate your virtual environment

In the terminal, run:

```bash
cd ~/fitwin-crewai
source .venv/bin/activate
```

You’ll see `(.venv)` again in your terminal.

3. Verify your environment

Run your tests to confirm everything’s working:

```bash
python -m pytest -q
```

4. Start your FastAPI server (optional)

```bash
uvicorn src.server.main:app --reload
```

Then visit http://127.0.0.1:8000/docs

---

### 🧩 Optional: Update and Sync with GitHub

If you made changes before your break, make sure they’re backed up.

```bash
git add .
git commit -m "work before break"
git push origin main
```

When you return:

```bash
git pull origin main
```

This ensures your local project matches your GitHub repository.

---

### 🧠 Quick Reference Commands

Task | Command
--- | ---
Stop the server | Ctrl + C
Deactivate venv | deactivate
Activate venv | source .venv/bin/activate
Run tests | python -m pytest -q
Start server | uvicorn src.server.main:app --reload
Push changes | git add . && git commit -m "message" && git push origin main
Pull latest changes | git pull origin main

---

### ✅ Notes

- You can safely close your laptop or VS Code anytime after stopping Uvicorn.
- Your `.venv` environment, Git repo, and files remain exactly as-is.
- You’ll never lose work if you commit and push before taking a break.

---

Last updated: October 2025
Project: FitTwin CrewAI
Maintainer: Laura Tornga (@rocketroz)
