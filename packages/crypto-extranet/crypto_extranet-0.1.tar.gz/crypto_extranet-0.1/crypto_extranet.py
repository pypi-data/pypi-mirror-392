"""Basic client for *.crypto-extranet.com extranets."""

import argparse
import base64
from pathlib import Path

import requests


class CryptoExtranet:
    """*.crypto-extranet.com client"""

    def __init__(self, url):
        self.url = url
        self.session = requests.session()
        self.session.headers.update({"User-Agent": "CryptoExtranet Python Client"})

    def authenticate(self, login, password):
        """Authenticate against the API.

        This just stores a cookie in self.session.
        """
        response = self.session.post(
            f"{self.url}/authenticate", json={"login": login, "password": password}
        )
        response.raise_for_status()

    def classeurs(self):
        """List directories (containing files)."""
        url = (
            f"{self.url}/api/extranet/coproprietaire/documents/classeur?"
            "sortColumn=date_commit&classeur=null&sortOrder=DESC"
        )
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["data"]["Classeurs"]

    def classeur(self, pk):
        """List files in a directory.

        `pk` is found from the self.classeurs() result
        """
        url = (
            f"{self.url}/api/extranet/coproprietaire/documents/classeur/{pk}?"
            "sortColumn=date_commit&classeur=null&sortOrder=DESC"
        )
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["data"]["Documents"]

    def download(self, pk, target_file: Path):
        """Download file with id `pk` to the target_file.

        `pk` is found in the `self.classeur()` result.
        """
        url = f"{self.url}/api/extranet/documents/downloadFile/{pk}"
        response = self.session.get(url)
        response.raise_for_status()
        json = response.json()
        target_file.write_bytes(base64.b64decode(json["base64"]))


def main():
    """Module entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("subdomain")
    parser.add_argument("login")
    parser.add_argument("password")
    args = parser.parse_args()

    extranet = CryptoExtranet(url=f"https://{args.subdomain}.crypto-extranet.com")
    extranet.authenticate(args.login, args.password)

    for classeur in extranet.classeurs():
        print(classeur["nom"])
        for file in extranet.classeur(classeur["id"]):
            target_directory = Path(classeur["nom"])
            target_file = target_directory / f"{file['title']}.pdf"
            print("   ", target_file)
            target_directory.mkdir(exist_ok=True)
            if not target_file.exists():
                extranet.download(file["id"], target_file)


if __name__ == "__main__":
    main()
