import argparse
import json
import os
from pathlib import Path
import requests as rq

BASE_URL = "https://anarchkey.pythonanywhere.com/"
INIT_ENDPOINT = "anarchkey_init"
INIT_FILENAME = ".anarchkey"


class AnarchKeyClient:
    """Client that fetches API keys from the AnarchKey service.

    Behavior additions:
    - On construction the client will attempt to read a local init token file
      at ~/.anarchkey and include it in every request as header
      'X-AnarchKey-Init'.
    """

    def __init__(self, api_key: str = "", username: str = "", password: str = ""):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.username = username
        self.password = password
        if os.path.exists(str(Path.home()) + "/.anarchkey"):
            self.token = str(open(str(Path.home()) + "/.anarchkey").read())
        else:
            self.token = ""
        self.init_file = Path.home() / INIT_FILENAME
        self.init_token = self._read_init_token()

    def _read_init_token(self):
        try:
            if self.init_file.exists():
                return self.init_file.read_text(encoding="utf-8").strip()
        except Exception:
            # if any read error occurs, ignore and return None
            pass
        return None

    def get_api_key(self, project_name: str):
        if self.token != "":
            payload = json.dumps({
                "project_name": project_name,
                "username": self.username,
                "api_key": self.api_key + self.token,
            })
        
            headers = {
                "Content-Type": "application/json"
            }
            if self.init_token:
                headers["X-AnarchKey-Init"] = self.init_token

            response = rq.request("POST", self.base_url + "get_api_key", headers=headers, data=payload)
            # try to parse JSON; if parsing fails return raw text
            try:
                response_json = response.json()
                # normalize response shape
                if isinstance(response_json, dict) and "api_key" in response_json:
                    return response_json["api_key"]
                return response_json
            except ValueError:
                return response.text
        else:
            return(Warning(" ERROR! : start your anarchkey service using the command:  anarchkey init --username YourName --password YourPassword"))


def do_init(base_url: str = BASE_URL, out_file: Path = None, username: str = None, password : str = None):
    """Call the anarchkey_init endpoint and write the returned token to a file.

    Returns the token that was written (or None on failure).
    """
    if out_file is None:
        out_file = Path.home() / INIT_FILENAME

    # If the token file already exists, skip contacting the server and
    # return the existing token.
    if out_file.exists():
        try:
            existing = out_file.read_text(encoding="utf-8").strip()
            # indicate that nothing was created by returning a tuple
            return existing, False
        except Exception:
            # fall through to attempt to recreate the file
            pass

    url = base_url + INIT_ENDPOINT
    payload = {}
    if username:
        payload["username"] = username
        payload["password"] = password

    print(payload)

    try:
        resp = rq.request("POST", url, json=payload, timeout=10)
    except Exception as e:
        raise RuntimeError(f"Failed to contact {url}: {e}")

    # Accept JSON token or plain-text
    token = None
    try:
        j = resp.json()
        # look for common fields
        for key in ("token", "secret", "key", "data"):
            if key in j:
                token = j[key]
                break
        # If top-level string-like
        if token is None and isinstance(j, str):
            token = j
    except ValueError:
        # not JSON, fall back to raw text
        token = resp.text

    if not token:
        raise RuntimeError("Init endpoint did not return a token")

    # ensure parent exists and write with restricted permissions
    try:
        out_file.write_text(str(token), encoding="utf-8")
        # set to user read/write only
        os.chmod(out_file, 0o600)
    except Exception as e:
        raise RuntimeError(f"Failed to write init token to {out_file}: {e}")

    # indicate that we created the token file
    return str(token), True


def main(argv=None):
    parser = argparse.ArgumentParser(prog="anarchkey", description="AnarchKey CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Initialize local token by calling anarchkey_init endpoint")
    p_init.add_argument("--base-url", default=BASE_URL, help="Base URL of the AnarchKey service")
    p_init.add_argument("--out-file", default=str(Path.home() / INIT_FILENAME), help="Path to write the init token")
    p_init.add_argument("--username", help=" username to send to the init endpoint")
    p_init.add_argument("--password", help=" password to send to the init endpoint")


    args = parser.parse_args(argv)
    if args.cmd == "init":
        try:
            token, created = do_init(base_url=args.base_url, out_file=Path(args.out_file), username=args.username, password=args.password)
            if created:
                print(f"Wrote init token to {args.out_file}")
            else:
                print(f"Init token already exists at {args.out_file}")
        except Exception as e:
            print(f"Error: {e}")
            return 2
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
