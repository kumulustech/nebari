import pathlib
from typing import List

import typer

from _nebari.config import read_configuration
from _nebari.deploy import deploy_configuration
from _nebari.render import render_template
from nebari.hookspecs import NebariStage, hookimpl
from nebari.schema import PostDeployHook

PAUSE_MESSAGE = "The deployment has paused after deploying stage {}.\n\nPress Enter to continue after deploying."


@hookimpl
def nebari_subcommand(cli: typer.Typer):
    @cli.command()
    def deploy(
        ctx: typer.Context,
        config_filename: pathlib.Path = typer.Option(
            ...,
            "--config",
            "-c",
            help="nebari configuration yaml file path",
        ),
        output_directory: pathlib.Path = typer.Option(
            "./",
            "-o",
            "--output",
            help="output directory",
        ),
        dns_provider: str = typer.Option(
            False,
            "--dns-provider",
            help="dns provider to use for registering domain name mapping",
        ),
        dns_auto_provision: bool = typer.Option(
            False,
            "--dns-auto-provision",
            help="Attempt to automatically provision DNS, currently only available for `cloudflare`",
        ),
        disable_prompt: bool = typer.Option(
            False,
            "--disable-prompt",
            help="Disable human intervention",
        ),
        disable_render: bool = typer.Option(
            False,
            "--disable-render",
            help="Disable auto-rendering in deploy stage",
        ),
        disable_checks: bool = typer.Option(
            False,
            "--disable-checks",
            help="Disable the checks performed after each stage",
        ),
        skip_remote_state_provision: bool = typer.Option(
            False,
            "--skip-remote-state-provision",
            help="Skip terraform state deployment which is often required in CI once the terraform remote state bootstrapping phase is complete",
        ),
        pause_after_stage: List[str] = typer.Option(
            [],
            "--pause-after-stage",
            help="Pause after specific stage(s), referenced by stage name",
        ),
    ):
        """
        Deploy the Nebari cluster from your [purple]nebari-config.yaml[/purple] file.
        """
        from nebari.plugins import nebari_plugin_manager

        stages = nebari_plugin_manager.ordered_stages
        config_schema = nebari_plugin_manager.config_schema

        config = read_configuration(config_filename, config_schema=config_schema)

        if not disable_render:
            render_template(output_directory, config, stages)

        def create_post_deploy_hooks(
            pause_after_stage: List[str] = pause_after_stage,
            stages: List[NebariStage] = stages,
        ):
            diff = set(pause_after_stage) - set([s.name for s in stages])
            if diff:
                raise ValueError(f"{diff} are not recognized stages.")

            post_deploy_hooks = []

            def _callback(stage_name):
                input(PAUSE_MESSAGE.format(stage_name))

            for s in pause_after_stage or []:
                post_deploy_hooks.append(PostDeployHook(name=s, callback=_callback))

            return post_deploy_hooks

        deploy_configuration(
            config,
            stages,
            post_deploy_hooks=create_post_deploy_hooks(),
            dns_provider=dns_provider,
            dns_auto_provision=dns_auto_provision,
            disable_prompt=disable_prompt,
            disable_checks=disable_checks,
            skip_remote_state_provision=skip_remote_state_provision,
        )
