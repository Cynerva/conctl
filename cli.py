#!/bin/env python3

import sys
import click
from subprocess import CompletedProcess

from typing import (
    List,
    Tuple,
    Dict,
    Optional
)

from conctl import getContainerRuntimeCtl


def pretty_print(proc: CompletedProcess) -> None:
    """
    Pretty print output from a process.

    :param proc: CompletedProcess
    :return: None
    """
    sys.stdout.write(
        proc.stdout.decode()
    )

    sys.stderr.write(
        proc.stderr.decode()
    )


@click.group()
@click.option('--force-runtime', default=None,
              type=click.Choice(['docker', 'containerd']),
              help='Force a runtime')
@click.option('--verbose', default=False, is_flag=True,
              help='Print additional information')
@click.pass_context
def cli(context: object,
        force_runtime: Optional[str],
        verbose: bool) -> None:
    """
    Base for the CLI.

    :param context: Object
    :param force_runtime: String
    :param verbose: Boolean
    :return: None
    """
    context.obj = getContainerRuntimeCtl(force_runtime)

    if verbose:
        print('Runtime {} selected'.format(
            context.obj.runtime))


@cli.command()
@click.option('--name', required=True,
              help='Name the container')
@click.option('--mount', required=False, multiple=True,
              help='Pass mounts in format `host:container`')
@click.option('--env', required=False, multiple=True,
              help='Pass env vars in format `key=value`')
@click.argument('image', required=True)
@click.argument('command', required=False)
@click.argument('args', required=False, nargs=-1)
@click.pass_obj
def run(ctl: object,
        name: str,
        mount: Tuple[str],
        env: Tuple[str],
        image: str,
        command: str,
        args: Tuple[str]) -> None:
    """
    Run a container.

    :return: None
    """
    mounts: Dict[str, str] = {}
    for m in mount:
        s: List[str] = m.split(':')
        try:
            mounts[s[0]] = s[1]
        except IndexError:
            sys.exit('{} is not a valid arg for mount'.format(s))

    environment: Dict[str, str] = {}
    for e in env:
        s: List[str] = e.splt('=')
        try:
            environment[s[0]] = [s[1]]
        except IndexError:
            sys.exit('{} is not a valid arg for env'.format(s))

    pretty_print(ctl.run(
        name=name,
        image=image,
        mounts=mounts,
        environment=environment,
        command=command,
        *args
    ))


@cli.command()
@click.argument('container_ids', required=False, nargs=-1)
@click.pass_obj
def delete(ctl: object,
           container_ids: Tuple[str]) -> None:
    """
    Delete containers.

    :return: None
    """
    pretty_print(ctl.delete(*container_ids))


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter