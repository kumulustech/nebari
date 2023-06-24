import pathlib
from typing import Any, Dict

from pydantic import BaseModel

from _nebari.provider import helm
from nebari.hookspecs import NebariStage


class HelmStageSchema(BaseModel):
    chart_name: str
    chart_repo: str
    chart_url: str
    chart_version: str
    chart_overrides: Dict[str, Any] = {}


class NebariHelmStage(NebariStage):
    stage_schema: HelmStageSchema

    @property
    def stage_prefix(self):
        return pathlib.Path("stages")

    def render(self) -> Dict[str, str]:
        # TODO:
        # - confirm kube context is appriopriately set
        # - return 'contents' dict, what to do if dry-run enabled?

        helm.helm_repo_add(self.stage_schema.chart_repo, self.stage_schema.chart_url)
        helm.helm_update()
        helm.helm_pull(
            self.stage_schema.chart_repo,
            self.stage_schema.chart_name,
            self.stage_schema.chart_version,
            self.stage_prefix,
        )
        values_path = self.stage_prefix / "values.yaml"
        helm.update_helm_values(self.stage_schema.chart_overrides, values_path)

    def deploy(self, stage_outputs: Dict[str, Dict[str, Any]]):
        pass

    def destroy(self, stage_outputs: Dict[str, Dict[str, Any]]):
        pass

    def check(self, stage_outputs: Dict[str, Dict[str, Any]]):
        pass

    def input_vars(self, stage_outputs: Dict[str, Dict[str, Any]]):
        pass


## Example usage

url = "https://charts.heartex.com/"
repo = "heartex"
chart = "label-studio"
version = "1.1.4"

schema = HelmStageSchema(
    chart_name=chart,
    chart_repo=repo,
    chart_url=url,
    chart_version=version,
    chart_overrides={
        "ci": True,
    },
)


class LabelStudioHelmStage(NebariHelmStage):
    stage_schema = schema
    priority = 100
    name = "label-studio"


class Config(BaseModel):
    pass


stage = LabelStudioHelmStage(".", Config())
stage.render()
