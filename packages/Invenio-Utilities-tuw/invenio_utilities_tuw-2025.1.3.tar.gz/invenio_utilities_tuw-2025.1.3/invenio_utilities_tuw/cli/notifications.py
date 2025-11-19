# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utilities for sending notifications."""

import sys

import click
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_config_tuw.tasks import send_outreach_emails as send_outreach_emails_task
from invenio_db import db


@click.group()
def notifications():
    """Utilities for sending notifications."""


@notifications.command("outreach")
@click.option(
    "-s",
    "--subject",
    default="Listen up buttercup!",
    help="Subject of the outreach email",
    type=str,
)
@click.option(
    "-S",
    "--sender",
    default=None,
    help="Address to set as sender of the email",
    type=str,
)
@click.option(
    "-H",
    "--html",
    "html_msg_file",
    help="HTML-formatted message to send",
    type=click.File("r"),
)
@click.option(
    "-m",
    "--message",
    "msg_file",
    help="Plaintext message to send",
    type=click.File("r"),
)
@click.option(
    "-t",
    "--sleep-time",
    "sleep_time",
    default=1,
    help="Time to wait after each email",
    type=float,
)
@click.option(
    "-n/-N",
    "--eager/--lazy",
    "send_now",
    default=True,
    help="Submit emails eagerly now or schedule it as background task",
)
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
@click.argument("users", nargs=-1)
@with_appcontext
def send_outreach_emails(
    users, subject, sender, html_msg_file, msg_file, sleep_time, send_now, yes
):
    """Send an outreach email to the specified users.

    Users are specified via their email addresses, which may contain SQL wildcards.
    For example, the following selects all registered TU Wien students:
    ``%@student.tuwien.ac.at``

    At least one of ``--message`` and ``--html`` has to be specified.
    The email will always be sent with both HTML-formatted and plain-text parts.
    If only one of the variants is given, simple transformations will be used to
    derive the other part's content.
    """
    html_msg = html_msg_file.read() if html_msg_file else None
    msg = msg_file.read() if msg_file else None
    if not html_msg and not msg:
        click.secho("Aborting: Neither '--message' nor '--html' are supplied", fg="red")
        sys.exit(1)

    resolved_users = set()
    for email_pattern in users:
        resolved_users.update(
            db.session.query(User).filter(User.email.like(email_pattern)).all()
        )
    users = sorted(resolved_users, key=lambda u: u.email)
    if not users:
        click.echo("Aborting: No users matched the specified email patterns")
        sys.exit(1)

    kwargs = {
        "subject": subject,
        "users": users if send_now else [u.email for u in users],
        "sleep_time": sleep_time,
        "retry_failed": True,
        "msg": msg,
        "html_msg": html_msg,
        "txt_msg": None,
        "sender": sender,
    }

    if not yes:
        click.secho("Review the email to be sent:", bold=True)
        click.secho(f"recipients = {[u.email for u in users]}", fg="green")
        click.secho(f"subject = {subject}", fg="yellow")
        if msg:
            click.secho(f"message = {msg}", fg="magenta")
        if html_msg:
            click.secho(f"html message = {html_msg}", fg="cyan")

        num_mails = len(users)
        approx_time = (num_mails - 1) * sleep_time
        click.confirm(
            f"Do you want to send {num_mails} emails? Estimated time: {approx_time}s",
            abort=True,
        )

    if send_now:
        successes, failures = send_outreach_emails_task(**kwargs)
        click.echo(f"{len(successes)} successful:")
        for success in successes:
            click.secho(success, fg="green")

        click.echo(f"{len(failures)} failed:")
        for failure in failures:
            click.secho(failure, fg="red")

        if failures:
            sys.exit(2)
    else:
        task = send_outreach_emails_task.delay(**kwargs)
        click.echo(
            f"Sending {len(users)} outreach emails via background task: {task.id}"
        )
