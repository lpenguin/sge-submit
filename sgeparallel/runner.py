import shutilwhich as shutil
from typing import List
import drmaa
import logging
import time


logger = logging.getLogger(__name__)


class JobTemplateParams:
    def __init__(self, job_name, stdout, stderr, join_streams, num_slots, work_dir):
        self.job_name = job_name
        self.stdout = stdout
        self.stderr = stderr
        self.join_streams = join_streams
        self.num_slots = num_slots
        self.work_dir = work_dir


class Runner:
    def __init__(self, session):
        # type: (drmaa.Session)->None
        self._session = session

    def submit_jobs(self, job_templates):
        # type: (List[drmaa.JobTemplate])->list
        job_ids = [
            self._session.runJob(jt)
            for jt in job_templates
        ]
        return job_ids

    def iter_results(self, job_ids):
        # type: (list)->None
        queued_ids = set(job_ids)

        run_count = None

        while True:
            try:
                res = self._session.wait(drmaa.Session.JOB_IDS_SESSION_ANY,
                                         timeout=drmaa.Session.TIMEOUT_NO_WAIT)
                queued_ids.remove(res.jobId)

                yield res
                continue
            except drmaa.ExitTimeoutException:
                pass
            except drmaa.errors.InvalidJobException:
                break
            time.sleep(0.1)
            statuses = ((job_id, self._session.jobStatus(job_id))
                        for job_id in queued_ids)
            running_statuses = [
                (job_id, status)
                for job_id, status in statuses
                if status == drmaa.JobState.RUNNING
                ]
            if len(running_statuses) != run_count:
                run_count = len(running_statuses)
                yield run_count

    def create_template(self, command, params):
        """

        :type command: list[str]
        :type params: dist[str, object]
        :rtype: drmaa.JobTemplate
        """

        jt = self._session.createJobTemplate()
        jt.remoteCommand = shutil.which(command[0])
        jt.args = command[1:]
        if params['num_slots'] > 1:
            jt.nativeSpecification = "-pe make {}".format(params['num_slots'])

        if params['stdout']:
            jt.outputPath = params['stdout']
        # if params['stderr']:
        jt.errorPath = ':/home/nprian/foo.err' #params['stderr']
        if params['join_streams']:
            jt.joinFiles = True
        if params['job_name']:
            jt.jobName = params['job_name']
        if params['work_dir']:
            jt.workingDirectory = params['work_dir']

        jt.params = params
        return jt

    def create_templates(self, commands_list, params_list):
        """
        :type commands_list:  list[list[str]]
        :type params_list:  list[dict[str, object]]
        :rtype: list[drmaa.JobTemplate]
        """

        return [self.create_template(command, params)
                for command, params in zip(commands_list, params_list)]




