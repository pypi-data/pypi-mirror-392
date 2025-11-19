# handsoff/cli.py
import argparse
import json
import os
from handsoff.modules.Commands_generate import Commands_generate

def load_settings(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(path, params):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=4, ensure_ascii=False)

def run():
    parser = argparse.ArgumentParser(prog="handsoff")

    parser.add_argument("--host")
    parser.add_argument("--port")
    parser.add_argument("--user")
    parser.add_argument("--server")
    parser.add_argument("--client")
    parser.add_argument("--pem")
    parser.add_argument("--env")
    parser.add_argument("--message")
    parser.add_argument("--repeat")

    parser.add_argument("command", choices=["run", "set", "pull", "push", "params"])

    parser.add_argument("extra", nargs="*")
    args = parser.parse_args()

    SETTINGS = os.path.join(os.path.dirname(__file__), "settings.json")
    settings = load_settings(SETTINGS)

    # CLI 옵션 우선 적용
    cli_params = {
        k: v for k, v in vars(args).items()
        if k in ["repeat", "message"] and v is not None
    }
    print(cli_params)

    cmd = Commands_generate(**cli_params)

    # if args.command == "set":
    #     save_settings(SETTINGS, cmd.get())
    #     return

    if args.command == "run":
        cmd.run()
        return
    else:
        print("Invalid command!")
        return