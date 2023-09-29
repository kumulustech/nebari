import json
import sys
import time
import typing
from typing import Any, Dict, List, Type
from urllib.parse import urlencode

import pydantic
from pydantic import Field

from _nebari import constants
from _nebari.stages.base import NebariTerraformStage
from _nebari.stages.tf_objects import (
    NebariHelmProvider,
    NebariKubernetesProvider,
    NebariTerraformState,
)
from _nebari.version import __version__
from nebari import schema
from nebari.hookspecs import NebariStage, hookimpl

# check and retry settings
NUM_ATTEMPTS = 10
TIMEOUT = 10  # seconds


class Storage(schema.Base):
    conda_store: str = "200Gi"
    shared_filesystem: str = "200Gi"

class Monitoring(schema.Base):
    enabled: bool = True

class InputSchema(schema.Base):
    storage: Storage = Storage()
    monitoring: Monitoring = Monitoring()


class OutputSchema(schema.Base):
    pass

# variables shared by multiple services
class KubernetesServicesInputVars(schema.Base):
    name: str
    environment: str
    endpoint: str
    node_groups: Dict[str, Dict[str, str]]


def _split_docker_image_name(image_name):
    name, tag = image_name.split(":")
    return {"name": name, "tag": tag}


class ImageNameTag(schema.Base):
    name: str
    tag: str

class MonitoringInputVars(schema.Base):
    monitoring_enabled: bool = Field(alias="monitoring-enabled")


class KubernetesServicesStage(NebariTerraformStage):
    name = "07-kubernetes-services"
    priority = 70

    input_schema = InputSchema
    output_schema = OutputSchema

    def tf_objects(self) -> List[Dict]:
        return [
            NebariTerraformState(self.name, self.config),
            NebariKubernetesProvider(self.config),
            NebariHelmProvider(self.config),
        ]

    def input_vars(self, stage_outputs: Dict[str, Dict[str, Any]]):
        domain = stage_outputs["stages/04-kubernetes-ingress"]["domain"]
        final_logout_uri = f"https://{domain}/hub/login"

        # Compound any logout URLs from extensions so they are are logged out in succession
        # when Keycloak and JupyterHub are logged out
        for ext in self.config.tf_extensions:
            if ext.logout != "":
                final_logout_uri = "{}?{}".format(
                    f"https://{domain}/{ext.urlslug}{ext.logout}",
                    urlencode({"redirect_uri": final_logout_uri}),
                )

        kubernetes_services_vars = KubernetesServicesInputVars(
            name=self.config.project_name,
            environment=self.config.namespace,
            endpoint=domain,
            node_groups=stage_outputs["stages/02-infrastructure"]["node_selectors"],
        )
        monitoring_vars = MonitoringInputVars(
            monitoring_enabled=self.config.monitoring.enabled,
        )
        return {
            **kubernetes_services_vars.dict(by_alias=True),
            **monitoring_vars.dict(by_alias=True),
        }

    def check(
        self, stage_outputs: Dict[str, Dict[str, Any]], disable_prompt: bool = False
    ):
        directory = "stages/07-kubernetes-services"
        import requests

        # suppress insecure warnings
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        def _attempt_connect_url(
            url, verify=False, num_attempts=NUM_ATTEMPTS, timeout=TIMEOUT
        ):
            for i in range(num_attempts):
                response = requests.get(url, verify=verify, timeout=timeout)
                if response.status_code < 400:
                    print(f"Attempt {i+1} health check succeeded for url={url}")
                    return True
                else:
                    print(f"Attempt {i+1} health check failed for url={url}")
                time.sleep(timeout)
            return False

        services = stage_outputs[directory]["service_urls"]["value"]
        for service_name, service in services.items():
            service_url = service["health_url"]
            if service_url and not _attempt_connect_url(service_url):
                print(
                    f"ERROR: Service {service_name} DOWN when checking url={service_url}"
                )
                sys.exit(1)


@hookimpl
def nebari_stage() -> List[Type[NebariStage]]:
    return [KubernetesServicesStage]
