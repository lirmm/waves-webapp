"""
Base Test class for Runner's adaptors
"""
from __future__ import unicode_literals

import time
import os
from django.utils.timezone import localtime
import waves.const
from waves.tests.base import WavesBaseTestCase
from waves.adaptors.base import JobRunnerAdaptor
from waves.adaptors.exceptions import *
from waves.exceptions.jobs import *
from waves.models import Service, Job, JobInput, Runner, RunnerParam
from waves.models.submissions import ServiceSubmission
from waves.tests.mocks.adaptor import MockJobRunnerAdaptor
import waves.settings
import logging

logger = logging.getLogger(__name__)

__all__ = ['TestBaseJobRunner', 'sample_runner']


def sample_runner(runner_impl):
    """
    Return a new adaptor model instance from adaptor class object
    Args:
        runner_impl: a JobRunnerAdaptor object
    Returns:
        Runner model instance
    """
    runner_model = Runner.objects.create(name=runner_impl.__class__.__name__,
                                         description='SubmissionSample Runner %s' % runner_impl.__class__.__name__,
                                         clazz='%s.%s' % (runner_impl.__module__, runner_impl.__class__.__name__),
                                         available=True)
    for name, value in runner_impl.init_params.items():
        # print 'name', name, 'value', value
        RunnerParam.objects.update_or_create(name=name, runner=runner_model, defaults={'default': value})
    return runner_model


def sample_job(service):
    """
    Return a new Job model instance for service
    Args:
        service: a Service model instance
    Returns:
        Job model instance
    """
    job = Job.objects.create(title='SubmissionSample Job', service=service)
    srv_submission = service.default_submission
    for srv_input in srv_submission.submission_inputs.all():
        job.job_inputs.add(JobInput.objects.create(srv_input=srv_input, job=job, value="fake_value"))
    return job


class TestBaseJobRunner(WavesBaseTestCase):
    """
    Test all functions in Runner adapters base class

    """
    current_result = None

    def _debug_job_state(self):
        logger.debug('Internal state %s, current %s', self.current_job._status, self.current_job.status)

    def setUp(self):
        # Create sample data
        super(TestBaseJobRunner, self).setUp()
        try:
            getattr(self, 'adaptor')
        except AttributeError:
            self.adaptor = MockJobRunnerAdaptor()
        self.runner_model = sample_runner(self.adaptor)
        self.service = Service.objects.create(name="SubmissionSample Service", runner=self.runner_model)
        self.service.submissions.add(ServiceSubmission.objects.create(label='samplesub', available_online=True,
                                                                      available_api=True, service=self.service))
        self.current_job = None
        self.jobs = []
        self._result = self.defaultTestResult()

    def tearDown(self):
        super(TestBaseJobRunner, self).tearDown()
        # if not waves.settings.WAVES_TEST_DEBUG:
        #    for job in self.jobs:
        #        job.delete_job_dirs()

    def run(self, result=None):
        self.current_result = result
        super(TestBaseJobRunner, self).run(result)

    def testConnect(self):
        # Only run for sub classes
        self.adaptor.connect()
        self.assertTrue(self.adaptor.connected)
        self.assertIsNotNone(self.adaptor._connector)
        self.adaptor.disconnect()
        self.assertFalse(self.adaptor.connected)

    def testWrongJobStates(self):
        """ Test exceptions raise when state inconsistency is detected in jobs
        """
        if not self.__class__.__name__ == 'TestBaseJobRunner':
            self.skipTest("Only run with mock adaptor, just check job states consistency")
        self.current_job = sample_job(self.service)

        with self.assertRaises(AdaptorInitError):
            self.adaptor = JobRunnerAdaptor(init_params=dict(unexpected_param='unexpected value'))

        self.jobs.append(self.current_job)
        self._debug_job_state()
        self.current_job.status = waves.const.JOB_RUNNING
        length1 = self.current_job.job_history.count()
        logger.debug('Test Prepare')
        self._debug_job_state()
        with self.assertRaises(JobInconsistentStateError):
            self.current_job.run_prepare()
        self._debug_job_state()
        logger.debug('Test Run')
        self.current_job.status = waves.const.JOB_UNDEFINED
        with self.assertRaises(JobInconsistentStateError):
            self.current_job.run_launch()
        self._debug_job_state()
        logger.debug('Test Cancel')
        self.current_job.status = waves.const.JOB_COMPLETED
        with self.assertRaises(JobInconsistentStateError):
            self.current_job.run_cancel()
            # self.adaptor.cancel_job(self.current_job)
        logger.debug('Internal state %s, current %s', self.current_job._status, self.current_job.status)
        # status hasn't changed
        self.assertEqual(self.current_job.status, waves.const.JOB_COMPLETED)
        logger.debug('%i => %s', len(self.current_job.job_history.values()), self.current_job.job_history.values())
        # assert that no history element has been added
        self.assertEqual(length1, self.current_job.job_history.count())
        self.current_job.status = waves.const.JOB_RUNNING
        self.current_job.run_cancel()
        self.assertTrue(self.current_job.status == waves.const.JOB_CANCELLED)

    def runJobWorkflow(self, job=None):
        if job is not None:
            self.current_job = job
        if self.current_job is None:
            self.current_job = sample_job(self.service)
        if self.current_job not in self.jobs:
            self.jobs.append(self.current_job)
        logger.info('Starting workflow process for job %s', self.current_job)
        self.assertGreaterEqual(self.current_job.job_history.count(), 1)
        # self.adaptor.prepare_job(self.current_job)
        self.current_job.run_prepare()
        self.assertEqual(self.current_job.status, waves.const.JOB_PREPARED)
        self.current_job.run_launch()
        # self.adaptor.run_job(self.current_job)
        logger.debug('Remote Job ID %s', self.current_job.remote_job_id)
        self.assertEqual(self.current_job.status, waves.const.JOB_QUEUED)
        for ix in range(100):
            # job_state = self.adaptor.job_status(self.current_job)
            job_state = self.current_job.run_status()
            logger.info(u'Current job state (%i) : %s ', ix, self.current_job.get_status_display())
            if job_state >= waves.const.JOB_COMPLETED:
                logger.info('Job state ended to %s ', self.current_job.get_status_display())
                break
            else:
                time.sleep(3)
        # self.assertIn(self.current_job.status, (waves.const.JOB_COMPLETED, waves.const.JOB_TERMINATED))
        if self.current_job.status in (waves.const.JOB_COMPLETED, waves.const.JOB_TERMINATED):
            # Get job run details
            # self.adaptor.job_run_details(self.current_job)
            self.current_job.run_details()
            history = self.current_job.job_history.first()
            logger.debug("History timestamp %s", localtime(history.timestamp))
            logger.debug("Job status timestamp %s", self.current_job.status_time)
            self.assertTrue(self.current_job.results_available)
            for output_job in self.current_job.job_outputs.filter(optional=False):
                # TODO reactivate job output verification as soon as possible
                if not os.path.isfile(output_job.file_path):
                    logger.warning("Job <<%s>> did not output expected %s (test_data/jobs/%s/) ",
                                   self.current_job.title, output_job.value, self.current_job.slug)

                self.assertTrue(os.path.isfile(output_job.file_path),
                                msg="Job <<%s>> did not output expected %s (test_data/jobs/%s/) " %
                                    (self.current_job.title, output_job.value, self.current_job.slug))
                logger.info("Expected output file: %s ", output_job.file_path)
            self.assertGreaterEqual(self.current_job.status, waves.const.JOB_COMPLETED)
        else:
            logger.warn('problem with job status %s', self.current_job.get_status_display())
        return True
