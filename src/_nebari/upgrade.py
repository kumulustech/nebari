import json
import logging
import re
import secrets
import string
from abc import ABC
from pathlib import Path

import rich
from pydantic.error_wrappers import ValidationError
from rich.prompt import Prompt

from _nebari.config import backup_configuration
from _nebari.utils import load_yaml, yaml
from _nebari.version import __version__, rounded_ver_parse
from nebari import schema

logger = logging.getLogger(__name__)

NEBARI_WORKFLOW_CONTROLLER_DOCS = (
    "https://www.nebari.dev/docs/how-tos/using-argo/#jupyterflow-override-beta"
)
ARGO_JUPYTER_SCHEDULER_REPO = "https://github.com/nebari-dev/argo-jupyter-scheduler"


def do_upgrade(config_filename, attempt_fixes=False):
    config = load_yaml(config_filename)
    if config.get("qhub_version"):
        rich.print(
            f"Your config file [purple]{config_filename}[/purple] uses the deprecated qhub_version key.  Please change qhub_version to nebari_version and re-run the upgrade command."
        )
        return

    try:
        from nebari.plugins import nebari_plugin_manager

        nebari_plugin_manager.read_config(config_filename)
        rich.print(
            f"Your config file [purple]{config_filename}[/purple] appears to be already up-to-date for Nebari version [green]{__version__}[/green]"
        )
        return
    except (ValidationError, ValueError) as e:
        if schema.is_version_accepted(config.get("nebari_version", "")):
            # There is an unrelated validation problem
            rich.print(
                f"Your config file [purple]{config_filename}[/purple] appears to be already up-to-date for Nebari version [green]{__version__}[/green] but there is another validation error.\n"
            )
            raise e

    start_version = config.get("nebari_version", "")
    print("start_version: ", start_version)

    UpgradeStep.upgrade(
        config, start_version, __version__, config_filename, attempt_fixes
    )

    # Backup old file
    backup_configuration(config_filename, f".{start_version or 'old'}")

    with config_filename.open("wt") as f:
        yaml.dump(config, f)

    rich.print(
        f"Saving new config file [purple]{config_filename}[/purple] ready for Nebari version [green]{__version__}[/green]"
    )

    ci_cd = config.get("ci_cd", {}).get("type", "")
    if ci_cd in ("github-actions", "gitlab-ci"):
        rich.print(
            f"\nSince you are using ci_cd [green]{ci_cd}[/green] you also need to re-render the workflows and re-commit the files to your Git repo:\n"
            f"   nebari render -c [purple]{config_filename}[/purple]\n"
        )


class UpgradeStep(ABC):
    _steps = {}

    version = ""  # Each subclass must have a version - these should be full release versions (not dev/prerelease)

    def __init_subclass__(cls):
        assert cls.version != ""
        assert (
            cls.version not in cls._steps
        )  # Would mean multiple upgrades for the same step
        cls._steps[cls.version] = cls

    @classmethod
    def has_step(cls, version):
        return version in cls._steps

    @classmethod
    def upgrade(
        cls, config, start_version, finish_version, config_filename, attempt_fixes=False
    ):
        """
        Runs through all required upgrade steps (i.e. relevant subclasses of UpgradeStep).
        Calls UpgradeStep.upgrade_step for each.
        """
        starting_ver = rounded_ver_parse(start_version or "0.0.0")
        finish_ver = rounded_ver_parse(finish_version)
        print("finish_ver: ", finish_ver)

        if finish_ver < starting_ver:
            raise ValueError(
                f"Your nebari-config.yaml already belongs to a later version ({start_version}) than the installed version of Nebari ({finish_version}).\n"
                "You should upgrade the installed nebari package (e.g. pip install --upgrade nebari) to work with your deployment."
            )

        step_versions = sorted(
            [
                v
                for v in cls._steps.keys()
                if rounded_ver_parse(v) > starting_ver
                and rounded_ver_parse(v) <= finish_ver
            ],
            key=rounded_ver_parse,
        )

        print("step_versions: ", step_versions)

        current_start_version = start_version
        for stepcls in [cls._steps[str(v)] for v in step_versions]:
            step = stepcls()
            config = step.upgrade_step(
                config,
                current_start_version,
                config_filename,
                attempt_fixes=attempt_fixes,
            )
            current_start_version = step.get_version()
            print("\n")

        return config

    def get_version(self):
        return self.version

    def requires_nebari_version_field(self):
        return rounded_ver_parse(self.version) > rounded_ver_parse("0.3.13")

    def upgrade_step(self, config, start_version, config_filename, *args, **kwargs):
        """
        Perform the upgrade from start_version to self.version.

        Generally, this will be in-place in config, but must also return config dict.

        config_filename may be useful to understand the file path for nebari-config.yaml, for example
        to output another file in the same location.

        The standard body here will take care of setting nebari_version and also updating the image tags.

        It should normally be left as-is for all upgrades. Use _version_specific_upgrade below
        for any actions that are only required for the particular upgrade you are creating.
        """
        finish_version = self.get_version()
        __rounded_finish_version__ = ".".join(
            [str(c) for c in rounded_ver_parse(finish_version)]
        )
        rich.print(
            f"\n---> Starting upgrade from [green]{start_version or 'old version'}[/green] to [green]{finish_version}[/green]\n"
        )

        # Set the new version
        if start_version == "":
            assert "nebari_version" not in config
        assert self.version != start_version

        if self.requires_nebari_version_field():
            rich.print(f"Setting nebari_version to [green]{self.version}[/green]")
            config["nebari_version"] = self.version

        def contains_image_and_tag(s: str) -> bool:
            # match on `quay.io/nebari/nebari-<...>:YYYY.MM.XX``
            pattern = r"^quay\.io\/nebari\/nebari-(jupyterhub|jupyterlab|dask-worker)(-gpu)?:\d{4}\.\d+\.\d+$"
            return bool(re.match(pattern, s))

        def replace_image_tag_legacy(image, start_version, new_version):
            start_version_regex = start_version.replace(".", "\\.")
            if not start_version:
                start_version_regex = "0\\.[0-3]\\.[0-9]{1,2}"

            docker_image_regex = re.compile(
                f"^([A-Za-z0-9_-]+/[A-Za-z0-9_-]+):v{start_version_regex}$"
            )

            m = docker_image_regex.match(image)
            if m:
                return ":".join([m.groups()[0], f"v{new_version}"])
            return None

        def replace_image_tag(s: str, new_version: str, config_path: str) -> str:
            legacy_replacement = replace_image_tag_legacy(s, start_version, new_version)
            if legacy_replacement:
                return legacy_replacement

            if not contains_image_and_tag(s):
                return s
            image_name, current_tag = s.split(":")
            if current_tag == new_version:
                return s
            loc = f"{config_path}: {image_name}"
            response = Prompt.ask(
                f"\nDo you want to replace current tag [green]{current_tag}[/green] with [green]{new_version}[/green] for:\n[purple]{loc}[/purple]? [Y/n] ",
                default="Y",
            )
            if response.lower() in ["y", "yes", ""]:
                return s.replace(current_tag, new_version)
            else:
                return s

        def set_nested_item(config: dict, config_path: list, value: str):
            config_path = config_path.split(".")
            for k in config_path[:-1]:
                try:
                    k = int(k)
                except ValueError:
                    pass
                config = config[k]
            try:
                config_path[-1] = int(config_path[-1])
            except ValueError:
                pass
            config[config_path[-1]] = value

        def update_image_tag(config, config_path, current_image, new_version):
            new_image = replace_image_tag(current_image, new_version, config_path)
            if new_image != current_image:
                set_nested_item(config, config_path, new_image)

            return config

        # update default_images
        for k, v in config.get("default_images", {}).items():
            config_path = f"default_images.{k}"
            config = update_image_tag(
                config, config_path, v, __rounded_finish_version__
            )

        # update profiles.jupyterlab images
        for i, v in enumerate(config.get("profiles", {}).get("jupyterlab", [])):
            current_image = v.get("kubespawner_override", {}).get("image", None)
            if current_image:
                config = update_image_tag(
                    config,
                    f"profiles.jupyterlab.{i}.kubespawner_override.image",
                    current_image,
                    __rounded_finish_version__,
                )

        # update profiles.dask_worker images
        for k, v in config.get("profiles", {}).get("dask_worker", {}).items():
            current_image = v.get("image", None)
            if current_image:
                config = update_image_tag(
                    config,
                    f"profiles.dask_worker.{k}.image",
                    current_image,
                    __rounded_finish_version__,
                )

        # Run any version-specific tasks
        return self._version_specific_upgrade(
            config, start_version, config_filename, *args, **kwargs
        )

    def _version_specific_upgrade(
        self, config, start_version, config_filename, *args, **kwargs
    ):
        """
        Override this method in subclasses if you need to do anything specific to your version.
        """
        return config


class Upgrade_0_3_12(UpgradeStep):
    version = "0.3.12"

    def _version_specific_upgrade(
        self, config, start_version, config_filename, *args, **kwargs
    ):
        """
        This version of Nebari requires a conda_store image for the first time.
        """
        if config.get("default_images", {}).get("conda_store", None) is None:
            newimage = "quansight/conda-store-server:v0.3.3"
            rich.print(
                f"Adding default_images: conda_store image as [green]{newimage}[/green]"
            )
            if "default_images" not in config:
                config["default_images"] = {}
            config["default_images"]["conda_store"] = newimage
        return config


class Upgrade_0_4_0(UpgradeStep):
    version = "0.4.0"

    def _version_specific_upgrade(
        self, config, start_version, config_filename: Path, *args, **kwargs
    ):

        if "terraform_modules" in config:
            del config["terraform_modules"]
            rich.print(
                "Removing terraform_modules field from config as it is no longer used.\n"
            )

        # project was never needed in Azure - it remained as PLACEHOLDER in earlier nebari inits!
        if "azure" in config:
            if "project" in config["azure"]:
                del config["azure"]["project"]

        # It is not safe to immediately redeploy without backing up data ready to restore data
        # since a new cluster will be created for the new version.
        # Setting the following flag will prevent deployment and display guidance to the user
        # which they can override if they are happy they understand the situation.
        config["prevent_deploy"] = True

        return config


class Upgrade_0_4_1(UpgradeStep):
    version = "0.4.1"

    def _version_specific_upgrade(
        self, config, start_version, config_filename: Path, *args, **kwargs
    ):
        return config


class Upgrade_2023_4_2(UpgradeStep):
    version = "2023.4.2"

    def _version_specific_upgrade(
        self, config, start_version, config_filename: Path, *args, **kwargs
    ):
        return config


class Upgrade_2023_7_2(UpgradeStep):
    version = "2023.7.2"

    def _version_specific_upgrade(
        self, config, start_version, config_filename: Path, *args, **kwargs
    ):

        return config


__rounded_version__ = ".".join([str(c) for c in rounded_ver_parse(__version__)])

# Manually-added upgrade steps must go above this line
if not UpgradeStep.has_step(__rounded_version__):
    # Always have a way to upgrade to the latest full version number, even if no customizations
    # Don't let dev/prerelease versions cloud things
    class UpgradeLatest(UpgradeStep):
        version = __rounded_version__
