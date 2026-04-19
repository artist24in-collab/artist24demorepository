#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
APPS_DIR = os.path.join(BASE_DIR, "apps")
LOG_PATH = os.path.join(BASE_DIR, "logs", "history.txt")


def list_templates():
    if not os.path.isdir(TEMPLATES_DIR):
        return []
    return [name for name in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, name))]


def create_app(app_name: str, template_name: str) -> str:
    if template_name not in list_templates():
        raise ValueError(f"Unknown template: {template_name}")

    destination = os.path.join(APPS_DIR, app_name)
    if os.path.exists(destination):
        raise FileExistsError(f"App already exists: {app_name}")

    os.makedirs(APPS_DIR, exist_ok=True)
    shutil.copytree(os.path.join(TEMPLATES_DIR, template_name), destination)
    record_history(app_name, template_name)
    return destination


def record_history(app_name: str, template_name: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(f"Created app '{app_name}' from template '{template_name}'\n")


def load_config() -> dict:
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Dev System - scaffold apps from templates")
    parser.add_argument("name", nargs="?", help="Name of the new app to create")
    parser.add_argument("--template", "-t", default=None, help="Template name to use")
    parser.add_argument("--list", action="store_true", help="List available templates")
    args = parser.parse_args()

    if args.list or args.name is None:
        templates = list_templates()
        print("Available templates:")
        for template in templates:
            print(f"- {template}")
        if args.name is None:
            sys.exit(0)

    config = load_config()
    template = args.template or config.get("default_template")
    try:
        output_path = create_app(args.name, template)
        print(f"Created app: {output_path}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
