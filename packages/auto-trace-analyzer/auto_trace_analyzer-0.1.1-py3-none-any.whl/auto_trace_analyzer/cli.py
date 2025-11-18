import sys
from typing import List
import click
from .runner import run_script

@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.argument("script", type=str)
@click.pass_context

def main(ctx: click.Context, script: str):

    script_args: List[str] = list(ctx.args)

    exit_code = run_script(script, script_args)

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
