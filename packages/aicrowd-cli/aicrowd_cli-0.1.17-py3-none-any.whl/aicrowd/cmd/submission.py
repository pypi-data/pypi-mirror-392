"""
Submission subcommand
"""
import json
import os
import tempfile

import click

from aicrowd.contexts import (
    ChallengeContext,
    ConfigContext,
    pass_challenge,
    pass_config,
)
from aicrowd.errors import INVALID_PARAMETER
from aicrowd.exceptions import CLIException
from aicrowd.utils import AliasedGroup, CommandWithExamples
from aicrowd.utils.utils import exception_handler


@click.group(name="submission", cls=AliasedGroup)
def submission_command():
    """
    Create and view submissions
    """


@click.command(
    name="create",
    cls=CommandWithExamples,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "-c",
    "--challenge",
    type=str,
    help="Specify challenge explicitly",
)
@click.option(
    "-f",
    "--file",
    "file_path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="The file to submit",
)
@click.option(
    "-d",
    "--description",
    type=str,
    help="Submission description",
    default="",
)
@click.option(
    "-t", "--tag", "submission_tag", type=str, help="[Git submissions] The tag to push"
)
@click.option(
    "--no-verify",
    is_flag=True,
    help="Disbale pre-submission sanity checks",
    default=False,
)
@pass_challenge
@pass_config
@click.pass_context
@exception_handler
def create_subcommand(
    click_ctx,
    config_ctx: ConfigContext,
    challenge_ctx: ChallengeContext,
    challenge: str,
    file_path: str,
    description: str,
    submission_tag: str,
    no_verify: bool,
):
    """
    Create a submission on AIcrowd

    You can use this same command to create both normal submissions and git based submissions.

    Examples:
      # submit a file for a challenge
      aicrowd submission create -c CHALLENGE -f submission.file -d "this is a sample submission"

      # or, you can create git submissions too
      # note that:
      #   1. no -f (the whole repo is submitted)
      #   2. no -c (the challenge is inferred from local git config)
      aicrowd submission create -t v3.0 -d "tried out some cool stuff"
    """
    from aicrowd.submission import create_submission

    extra_args = {}
    for arg in click_ctx.args:
        if "=" in arg:
            key, val = arg.split("=", 1)[:2]
            extra_args[key] = val

    print(
        create_submission(
            challenge,
            file_path,
            description,
            True,
            submission_tag,
            config_ctx,
            challenge_ctx,
            no_verify,
            **extra_args
        )
    )


submission_command.add_command(create_subcommand)


def _parse_model_kwargs(raw_args):
    model_kwargs = {}
    i = 0

    while i < len(raw_args):
        token = raw_args[i]

        if token.startswith("--"):
            stripped = token[2:]
            if not stripped:
                raise CLIException(
                    "Invalid kwarg format.",
                    "Use --key value or --key=value.",
                    INVALID_PARAMETER,
                )
            if "=" in stripped:
                key, value = stripped.split("=", 1)
            else:
                i += 1
                if i >= len(raw_args):
                    raise CLIException(
                        f"Missing value for option '--{stripped}'.",
                        "Provide a value like --key value.",
                        INVALID_PARAMETER,
                    )
                key = stripped
                value = raw_args[i]
        elif "=" in token:
            key, value = token.split("=", 1)
        else:
            raise CLIException(
                f"Unable to parse kwarg '{token}'.",
                "Use --key value or key=value.",
                INVALID_PARAMETER,
            )

        normalized_key = key.replace("-", "_")
        if not normalized_key:
            raise CLIException(
                "Empty kwarg name detected.",
                "Ensure options have names, e.g. --hf_repo value.",
                INVALID_PARAMETER,
            )

        model_kwargs[normalized_key] = value
        i += 1

    if not model_kwargs:
        raise CLIException(
            "You must provide at least one kwarg for submit-model.",
            "Add options like --hf_repo <repo> or --hf-token <token>.",
            INVALID_PARAMETER,
        )

    return model_kwargs


@click.command(
    name="submit-model",
    cls=CommandWithExamples,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "-c",
    "--challenge",
    type=str,
    required=True,
    help="Specify challenge explicitly",
)
@click.option(
    "-d",
    "--description",
    type=str,
    help="Submission description",
    default="",
)
@pass_challenge
@pass_config
@click.pass_context
@exception_handler
def submit_model_command(
    click_ctx,
    config_ctx: ConfigContext,
    challenge_ctx: ChallengeContext,
    challenge: str,
    description: str,
):
    """
    Submit a model configuration JSON as a file-based submission.

    Examples:
      aicrowd submit-model -c CHALLENGE --description "HF model" --hf_repo org/repo --hf-token token123 --max_steps 1000
    """
    from aicrowd.submission import create_submission

    model_kwargs = _parse_model_kwargs(list(click_ctx.args))

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp_file:
            json.dump(model_kwargs, tmp_file)
            tmp_file.flush()
            tmp_path = tmp_file.name

        print(
            create_submission(
                challenge,
                tmp_path,
                description,
                True,
                None,
                config_ctx,
                challenge_ctx,
                True,
            )
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
