# /// script
# dependencies = [
#   "requests",
# ]
# ///
import argparse
import os

import requests

from nested.test import check_imported


def get_oidc_token(backend_url):
    # GitHub natively injects these into the composite runner shell environment
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")

    if not request_token or not request_url:
        raise RuntimeError(
            "OIDC environment variables not found. "
            "Did you forget to add 'permissions: id-token: write' to the consuming workflow?"
        )

    params = {"audience": backend_url}
    headers = {"Authorization": f"Bearer {request_token}"}

    response = requests.get(request_url, params=params, headers=headers)
    response.raise_for_status()

    return response.json().get("value")


def main():
    # Parse the backend-url passed from action.yml env configuration
    check_imported()
    return
    backend_url = os.environ.get("INPUT_BACKEND_URL")

    try:
        print("Fetching secure OIDC Token from GitHub...")
        oidc_token = get_oidc_token(backend_url)

        # Capture standard GitHub metadata properties injected automatically by the runner
        # payload = {
        #     "token": oidc_token,
        #     "repository": os.environ.get("GITHUB_REPOSITORY"),
        #     "repository_owner": os.environ.get("GITHUB_REPOSITORY_OWNER"),
        #     "sha": os.environ.get("GITHUB_SHA"),
        # }

        # payload = {"token": oidc_token, "env": dict(os.environ)}

        # print(payload)

        print(
            f"Payload successfully prepared! Transmitting to queue at {backend_url}..."
        )

        assert backend_url
        # Uncomment this line when your backend route is live:
        response = requests.post(
            backend_url,
            headers={"Authorization": f"Bearer {oidc_token}"},
            json={"sample": "data"},
        )
        response.raise_for_status()

        print("Success! Job successfully placed in the backend queue.")
        print(response.json().get("message"))

    except Exception as e:
        print(f"::error::Action script execution failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
