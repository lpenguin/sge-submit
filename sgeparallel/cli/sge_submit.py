from __future__ import absolute_import, print_function


import argparse
import os
import tempfile
import threading

import drmaa
import signal


from sgeparallel.runner import Runner
from sgeparallel.template import command_substitute, params_substitute
from sgeparallel.util import iter_stdin, has_stdin
from sgeparallel.cli.progress import submit_and_print_progress, print_progress
from sgeparallel.cli.argparser import sge_params_dict, sge_params_parser
from tailer import follow


def create_templates_from_args(runner, params, args):
    tpl = runner.create_template(args.cmd_args, params)
    return [tpl]


def create_templates_from_stdin(runner, params, args):
    replacements = list(iter_stdin())

    commands_list = [
        command_substitute(args.cmd_args, repl)
        for repl in replacements
        ]

    params_list = [
        params_substitute(params, repl)
        for repl in replacements
        ]
    job_tpls = runner.create_templates(commands_list=commands_list,
                                       params_list=params_list)

    return job_tpls


def print_template(tpl):
    # type: (drmaa.JobTemplate) -> None
    print("# wd: {wd}, stdout: {stdout}, stderr: {stderr}, join_streams: {join_streams}, num slots: {num_slots}".format(
        wd=tpl.params['work_dir'],
        stdout=tpl.params['stdout'],
        stderr=tpl.params['stderr'],
        join_streams=tpl.params['join_streams'],
        num_slots=tpl.params['num_slots'],
    ))
    print("{cmd} {arguments}".format(
        cmd=tpl.remoteCommand,
        arguments=' '.join(tpl.args)
    ))


def process_single_command(runner, params, args):
    tpl = runner.create_template(args.cmd_args, params)

    if args.no_progress:
        runner.submit_jobs([tpl])
    else:
        submit_and_print_progress(runner=runner, job_tpls=[tpl])


def process_many_commands(runner, params, args):
    replacements = list(iter_stdin())

    commands_list = [
        command_substitute(args.cmd_args, repl)
        for repl in replacements
    ]

    params_list = [
        params_substitute(params, repl)
        for repl in replacements
    ]

    if args.dry_run:
        for cmd in commands_list:
            print(' '.join(cmd))
        return
    job_tpls = runner.create_templates(commands_list=commands_list,
                                       params_list=params_list)
    if args.no_progress:
        runner.submit_jobs(job_tpls)
    else:
        submit_and_print_progress(runner=runner, job_tpls=job_tpls)


def main():
    p = argparse.ArgumentParser(parents=[sge_params_parser()])

    p.add_argument('-n', '--dry-run', action='store_true')
    p.add_argument('-W', '--watch', action='store_true')

    p.add_argument('cmd_args', nargs=argparse.REMAINDER)

    args = p.parse_args()
    params = sge_params_dict(args)

    with drmaa.Session() as session:
        def sigint(signal, frame):
            print()
            print(session.contact)
            exit(1)
        signal.signal(signal.SIGINT, sigint)

        runner = Runner(session)

        if args.watch:
            tmpl_file = tempfile.NamedTemporaryFile(prefix="session_out", dir='/home/nprian').name
            params['stdout'] = ':'+tmpl_file
            params['join_streams'] = True
            with open(tmpl_file, 'w') as f: pass

        if has_stdin():
            tpls = create_templates_from_stdin(
                runner=runner,
                params=params,
                args=args,
            )
        else:
            tpls = create_templates_from_args(
                runner=runner,
                params=params,
                args=args,
            )

        if args.dry_run:
            for t in tpls:
                print_template(t)
            exit(0)

        job_ids = runner.submit_jobs(tpls)

        if args.watch:
            t = threading.Thread(target=tailfile, args=(tmpl_file,))
            t.setDaemon(True)
            t.start()
            session.synchronize(job_ids)
            os.remove(tmpl_file)
        elif not args.progress:
            print(session.contact)
            exit(0)
        else:
            print_progress(runner, job_ids)


def tailfile(tmpl_file):
    with open(tmpl_file) as f:
        for l in follow(f):
            print(l)
