import os
import subprocess
from datetime import datetime
import shutil
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "ai_mode": True,
    "models": ["mistral", "tinyllama"],
    "auto_suggest": True,
    "fallback_enabled": True
}

def ask_ai(command):
    models = CONFIG["models"]

    # Load planner rules
    planner_path = os.path.join(BASE_DIR, "agents", "planner.txt")
    planner_rules = ""

    if os.path.exists(planner_path):
        with open(planner_path, "r") as f:
            planner_rules = f.read()

    prompt = f"""
{planner_rules}

USER REQUEST:
{command}

TASK:

You must respond ONLY in valid JSON format.

Structure:
{{
  "plan": "short explanation",
  "files": [
    {{ "path": "index.html", "content": "<html>...</html>" }},
    {{ "path": "style.css", "content": "..." }},
    {{ "path": "app.js", "content": "..." }}
  ],
  "actions": [
    {{ "type": "deploy_vercel" }},
    {{ "type": "setup_database", "provider": "supabase" }},
    {{ "type": "setup_auth", "provider": "firebase" }}
  ],
  "suggestions": [
    "free hosting: vercel",
    "free database: supabase",
    "free auth: firebase"
  ]
}}

RULES:
- Always include full working code
- Keep UI clean and modern
- Use HTML, CSS, JS
- Add comments
- If something is not possible → suggest free alternative
- Keep everything beginner-friendly
"""

    for model in models:
        try:
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            output = result.stdout.decode()

            if output.strip():
                print(f"✅ Used model: {model}")
                return output

        except:
            continue

    return None

def create_project(command):
    name = command.lower().replace(" ", "_")[:30]
    project_path = os.path.join(BASE_DIR, "apps", name)

    os.makedirs(project_path, exist_ok=True)

    if CONFIG["ai_mode"]:
        project_path = "./workspace"  # or your project folder
        os.makedirs(project_path, exist_ok=True)

        output = ask_ai(command)

        if output:
            execute_ai_output(output, project_path)
        elif CONFIG["fallback_enabled"]:
            print("⚠️ AI failed, using template fallback")
            template = choose_template(command)
            copy_template(template, project_path)
            create_readme(project_path, command)
        else:
            print("⚠️ AI failed, no fallback enabled")
    elif CONFIG["fallback_enabled"]:
        print("🤖 Using template fallback...")
        template = choose_template(command)
        copy_template(template, project_path)
        create_readme(project_path, command)
    else:
        print("⚠️ AI mode disabled, no fallback enabled")

    clean_project(project_path)
    log(command, project_path)

    print(f"✅ Done: {project_path}")

def execute_ai_output(output, project_path):
    try:
        data = json.loads(output)
    except:
        print("❌ Failed to parse AI output")
        return

    # ---- SAVE FILES ----
    if "files" in data:
        for file in data["files"]:
            path = os.path.join(project_path, file["path"])
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(file["content"])

            print(f"✅ Created: {file['path']}")

    # ---- RUN ACTIONS ----
    if "actions" in data:
        for action in data["actions"]:
            run_action(action, project_path)

    # ---- SAVE INFO ----
    with open(os.path.join(project_path, "AI_INFO.txt"), "a") as f:
        f.write(json.dumps(data, indent=2) + "\n")

    print("🚀 Done.")

def run_action(action, project_path):
    action_type = action.get("type")

    print(f"⚙️ Running action: {action_type}")

    if action_type == "deploy_vercel":
        try:
            subprocess.run(
                ["vercel", "--prod", "--yes"],
                cwd=project_path
            )
        except:
            print("❌ Vercel deploy failed")

    elif action_type == "setup_database":
        provider = action.get("provider", "supabase")
        print(f"🗄️ Suggest using {provider} (manual setup required)")

    elif action_type == "setup_auth":
        provider = action.get("provider", "firebase")
        print(f"🔐 Suggest using {provider} (manual setup required)")

    else:
        print(f"⚠️ Unknown action: {action_type}")

def save_project_config(project_path, config):
    path = os.path.join(project_path, "project.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)

def clean_project(path):
    # Ensure basic files exist
    required = ["index.html", "style.css", "app.js"]

    for file in required:
        file_path = os.path.join(path, file)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"// {file} placeholder")

def create_readme(path, command):
    with open(os.path.join(path, "README.md"), "w") as f:
        f.write(f"# {command}\n\nGenerated by AI system.\n")

def choose_template(command):
    if "3d" in command.lower():
        return "templates/3d-app-template"
    return "templates/webapp-template"

def copy_template(template_path, project_path):
    full_path = os.path.join(BASE_DIR, template_path)

    if os.path.exists(full_path):
        for item in os.listdir(full_path):
            s = os.path.join(full_path, item)
            d = os.path.join(project_path, item)

            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

def log(command, path):
    with open(os.path.join(BASE_DIR, "logs", "history.txt"), "a") as f:
        f.write(f"{datetime.now()} | {command} -> {path}\n")

if __name__ == "__main__":
    cmd = input("Enter your command: ")
    create_project(cmd)
