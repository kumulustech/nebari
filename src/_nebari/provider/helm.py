import collections.abc
import logging
import os
import platform
import tarfile
import tempfile
from pathlib import Path
from typing import Any, Dict, Union
from urllib.parse import urljoin

import requests
from ruamel.yaml import YAML

from _nebari.utils import run_subprocess_cmd

logger = logging.getLogger(__name__)


class HelmException(Exception):
    pass


def install_helm_binary(version="v3.12.1"):
    base = "https://get.helm.sh"
    helm = "helm"
    helm_path = f"{platform.system().lower()}-{platform.machine()}"
    download_url = urljoin(base, f"helm-{version}-{helm_path}.tar.gz")

    helm_dir = Path(tempfile.gettempdir()) / helm / version
    helm_dir.mkdir(parents=True, exist_ok=True)
    final_path = helm_dir / helm

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
    helm_path = install_helm_binary()
    logger.info(f" helm at {helm_path}")
    if run_subprocess_cmd([helm_path] + processargs, **kwargs):
        raise HelmException("Helm returned an error")


def helm_repo_add(name: str, url: str):
    run_helm_subprocess(["repo", "add", name, url])


def helm_update():
    run_helm_subprocess(["repo", "update"])


def helm_pull(repo: str, chart: str, version: str, output_directory: Union[str, Path]):
    if isinstance(output_directory, str):
        output_directory = Path(output_directory)

    if (output_directory / chart).exists():
        logger.info(f"chart {chart} already exists in {output_directory}, skipping")
        return
    elif not output_directory.exists():
        output_directory.mkdir(parents=True, exist_ok=True)

    run_helm_subprocess(
        [
            "pull",
            f"{repo}/{chart}",
            "--version",
            version,
            "--untar",
            "--untardir",
            output_directory,
        ]
    )


def update_helm_values(overrides: Dict[str, Any], filepath: Union[str, Path]):
    yaml = YAML()

    with open(filepath, "r") as f:
        values = yaml.load(f)

    def update(d, u):
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    values = update(values, overrides)

    with open(filepath, "w") as f:
        yaml.dump(values, f)


## Example usage

# url = "https://charts.heartex.com/"
# repo = "heartex"
# chart = "label-studio"
# version = "1.1.4"

# helm_repo_add(repo, url)
# helm_update()
# helm_pull(repo, chart, version, ".")
