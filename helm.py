import logging
import os
import platform
import tarfile
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import requests

from _nebari.utils import run_subprocess_cmd

logger = logging.getLogger(__name__)


class HelmException(Exception):
    pass


def download_helm_binary(version="v3.12.1"):
    base = "https://get.helm.sh"
    helm = "helm"
    helm_path = f"{platform.system().lower()}-{platform.machine()}"
    download_url = urljoin(base, f"helm-{version}-{helm_path}.tar.gz")

    final_path = Path(tempfile.gettempdir()) / helm / version
    final_path.mkdir(parents=True, exist_ok=True)
    final_path = final_path / helm

    if not final_path.is_file():
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            file_path = tmp_dir / f"{helm}.tar.gz"

            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(path=tmp_dir)

            # move the helm binary to final_path
            binary_path = tmp_dir / helm_path / helm
            binary_path.rename(final_path)

    os.chmod(final_path, 0o555)
    return final_path


def run_helm_subprocess(processargs, **kwargs):
    helm_path = download_helm_binary()
    logger.info(f" helm at {helm_path}")
    if run_subprocess_cmd([helm_path] + processargs, **kwargs):
        raise HelmException("Helm returned an error")
