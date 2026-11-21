# NotOpenAI: a tiny client for the Code in Place AI server.
# It copies the shape of the OpenAI library, but it uses your Code in Place
# key, so you don't need an OpenAI account. You never need to edit this file.
import json
import os
import ssl
import urllib.error
import urllib.request

URL = "https://us-central1-codeinplace-production.cloudfunctions.net/notopenaiv2"

# Python from python.org on a Mac doesn't know the system's certificates, so it
# can't check who it is talking to. We ship a list of trusted certificates in
# this folder and use it as well as the system's own.
CA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cacert.pem")


def _ssl_context():
    context = ssl.create_default_context()  # the system's certificates, if any
    context.load_verify_locations(CA_FILE)  # plus our own copy
    return context


class NotOpenAIError(Exception):
    def __init__(self, code, message, retry_after=None):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


class Usage:
    def __init__(self, data):
        self.input_tokens = data["input_tokens"]
        self.output_tokens = data["output_tokens"]
        self.reasoning_tokens = data["output_tokens_details"]["reasoning_tokens"]
        self.total_tokens = data["total_tokens"]


class Response:
    def __init__(self, data):
        self.id = data.get("id")
        self.status = data["status"]
        self.output_text = data["output_text"]
        self.usage = Usage(data["usage"])
        self.remaining_tokens = data["remaining_tokens"]


class Responses:
    def __init__(self, client):
        self._client = client

    def create(self, input, model="gpt-5-nano", **kwargs):
        body = {"model": model, "input": input, **kwargs}
        data = self._client._request("POST", body)
        response = Response(data)
        if response.status == "incomplete" and not response.output_text:
            raise NotOpenAIError(
                "incomplete",
                "The model ran out of output tokens before answering. Try a "
                "shorter request, or reasoning={'effort': 'minimal'}.",
            )
        return response


class NotOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.responses = Responses(self)

    def usage(self):
        return self._request("GET")

    def _request(self, method, body=None):
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            URL,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "notopenai-python",
            },
        )
        try:
            with urllib.request.urlopen(
                request, timeout=120, context=_ssl_context()
            ) as reply:
                return json.loads(reply.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            # The server answered with an error. Its message is written for
            # students, so pass it along.
            text = error.read().decode("utf-8", errors="replace")
            try:
                details = json.loads(text).get("error", {})
            except (ValueError, AttributeError):
                details = {}
            raise NotOpenAIError(
                details.get("code", "error"),
                details.get("message", text or "The server sent an error."),
                error.headers.get("Retry-After"),
            ) from None
        except urllib.error.URLError as error:
            if isinstance(error.reason, ssl.SSLCertVerificationError):
                raise NotOpenAIError(
                    "certificate",
                    "Python couldn't verify the server's security certificate. "
                    "If you're on a school or work network, try a different one, "
                    "and tell us on the forum if it keeps happening.",
                ) from None
            raise NotOpenAIError(
                "network",
                "Couldn't reach the server. Check your internet connection and try again.",
            ) from None
        except TimeoutError:
            raise NotOpenAIError(
                "network", "The server took too long to answer. Try again."
            ) from None
