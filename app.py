import json
import math
import os
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent
MAX_DESCRIPTION_LENGTH = 30_000


def remaining_weekdays(deadline, today=None):
    today = today or date.today()
    current = today + timedelta(days=1)
    if current > deadline:
        return 0
    span = (deadline - current).days + 1
    full_weeks, remaining_days = divmod(span, 7)
    count = full_weeks * 5
    return count + sum(
        (current.weekday() + offset) % 7 < 5
        for offset in range(remaining_days)
    )


def load_api_key():
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key

    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() == "TYPESAFE_API_KEY":
                return value.strip().strip("\"'")
    return None


class DemoHandler(BaseHTTPRequestHandler):
    def call_typesafe(self, api_key, payload):
        request = Request(
            "https://api.typesafe.ai/v1/systemone",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read())

    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        page = (ROOT / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        if self.path != "/estimate":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_DESCRIPTION_LENGTH + 100:
                self.respond_json(400, {"error": "Description is empty or too long."})
                return
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                self.respond_json(400, {"error": "Expected a ticket description and deadline."})
                return
            description = body.get("description")
            if not isinstance(description, str):
                self.respond_json(400, {"error": "Enter a ticket description under 30,000 characters."})
                return
            description = description.strip()
            if not description or len(description) > MAX_DESCRIPTION_LENGTH:
                self.respond_json(400, {"error": "Enter a ticket description under 30,000 characters."})
                return
            try:
                deadline = date.fromisoformat(body.get("deadline", ""))
            except (TypeError, ValueError):
                self.respond_json(400, {"error": "Choose a valid deadline date."})
                return

            api_key = load_api_key()
            if not api_key:
                self.respond_json(500, {"error": "Set TYPESAFE_API_KEY in your environment or .env file."})
                return

            today = date.today()
            available_workdays = remaining_weekdays(deadline, today)
            result = self.call_typesafe(api_key, {
                "model": "jev-latest",
                "state": {
                    "ticket_description": description,
                    "today": today.isoformat(),
                    "deadline": deadline.isoformat(),
                    "available_workdays_before_deadline": available_workdays,
                    "schedule_assumption": (
                        "Assume one engineer works full-time on the ticket on weekdays. Available workdays "
                        "exclude today and weekends; public holidays are not accounted for."
                    ),
                },
                "questions": {
                    "will_meet_deadline": {
                        "type": "noul",
                        "instructions": (
                            "Estimate the probability that this ticket will be completed by the stated "
                            "deadline, given the ticket description, today's date, available workdays, and "
                            "schedule assumption. Consider the scope, complexity, uncertainty, and any "
                            "explicit effort breakdown in the ticket. An effort breakdown is evidence about "
                            "work required, not elapsed waiting time. Return the probability of meeting the "
                            "deadline, not a guarantee."
                        ),
                        "criteria": {
                            "true": "The ticket will be completed by the deadline.",
                            "false": "The ticket will not be completed by the deadline.",
                        },
                    }
                },
            })
            likelihood = float(result["answers"]["will_meet_deadline"]["noul"])
            if not math.isfinite(likelihood) or not 0 <= likelihood <= 1:
                raise ValueError("Invalid deadline probability.")
            self.respond_json(200, {
                "deadline_likelihood": likelihood,
                "available_workdays": available_workdays,
                "deadline": deadline.isoformat(),
                "model": result.get("model"),
            })
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            self.respond_json(error.code, {"error": f"TypeSafe API error ({error.code}).", "detail": detail})
        except (URLError, TimeoutError):
            self.respond_json(502, {"error": "Could not reach the TypeSafe API. Try again shortly."})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.respond_json(502, {"error": "The estimate response was not in the expected format."})

    def respond_json(self, status, data):
        encoded = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        # Avoid logging request data or credentials in the local demo.
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), DemoHandler)
    print("Ticket effort demo available at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
