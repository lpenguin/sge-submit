import drmaa
from sgeparallel.runner import Runner
from sgeparallel.util import progress_bar


def submit_and_print_progress(runner, job_tpls):
    """

    :type runner: Runner
    :type job_tpls: list[drmaa.JobTemplate]
    """

    ids = runner.submit_jobs(job_tpls)
    print("Submitted {} jobs".format(len(job_tpls)))
    running = 0
    done = 0
    for r in runner.iter_results(ids):
        if isinstance(r, drmaa.JobInfo):
            # t.update()
            done += 1
            pass
        else:
            running = r
        progress_bar(iteration=done,
                     running=running,
                     total=len(job_tpls))



def print_progress(runner, job_ids):
    """

    :type runner: Runner
    :type job_tpls: list[drmaa.JobTemplate]
    """

    print("Submitted {} jobs".format(len(job_ids)))
    running = 0
    done = 0
    for r in runner.iter_results(job_ids):
        if isinstance(r, drmaa.JobInfo):
            # t.update()
            done += 1
            pass
        else:
            running = r
        progress_bar(iteration=done,
                     running=running,
                     total=len(job_ids))
