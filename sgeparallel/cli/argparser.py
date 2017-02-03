import argparse
import os
from os.path import join


def prepend_with_double_colon(s):
    if not s:
        return s
    return s if s.startswith(':') else ':'+s


def sge_params_parser():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('-p', '--num-slots', default=1, type=int)
    p.add_argument('-o', '--stdout', default='', type=prepend_with_double_colon)
    p.add_argument('-e', '--stderr', default='', type=prepend_with_double_colon)
    p.add_argument('-s', '--join-streams', action='store_true')
    p.add_argument('-j', '--job-name', default='')
    p.add_argument('-w', '--work-dir', default='')
    p.add_argument('-P', '--progress', action='store_true')

    return p


def sge_params_dict(args):
    wd = os.getcwd() if not args.work_dir else args.work_dir
    if wd and not wd.startswith('/'):
        wd = join(os.getcwd(), wd)
    return dict(
        num_slots=args.num_slots,
        stdout=args.stdout,
        stderr=args.stderr,
        join_streams=args.join_streams,
        job_name=args.job_name,
        work_dir=wd
    )

