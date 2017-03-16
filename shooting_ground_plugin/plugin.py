import logging

from yandextank.common.interfaces import (
    AbstractPlugin,
    MonitoringDataListener,
    AggregateResultListener,
)
from .client import ShootingGroundClient

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin, AggregateResultListener, MonitoringDataListener):
    """
    Plugin to automatically send load test data to ShootingGround service.
    """
    SECTION = 'shooting_ground'

    def __init__(self, core):
        super(Plugin, self).__init__(core)
        self.locks_list_dict = {}
        self.api_client = ShootingGroundClient()
        self.target = None
        self.lock_target_duration = None
        self.locks_list_cfg = None
        self.job_name = None
        self.ignore_target_lock = None
        self.job_id = None
        self.test_start_time = None

    @staticmethod
    def get_key():
        return __file__

    def get_available_options(self):
        return [
            'api_address',
            'api_timeout',
            'job_name',
            'token_file',
        ]

    @staticmethod
    def read_token(filename):
        # TODO
        return ''

    def configure(self):
        aggregator = self.core.job.aggregator_plugin
        aggregator.add_result_listener(self)

        self.api_client.set_api_address(self.get_option('api_address'))
        self.api_client.set_api_timeout(self.get_option('api_timeout', 30))
        self.api_client.set_api_token(self.read_token(self.get_option('token_file', '')))
        self.job_name = unicode(self.get_option('job_name', '').decode('utf8'))

    def start_test(self):
        # TODO initialize job
        self.job_id = self.api_client.create_job(self.job_name)

    def end_test(self, retcode):
        # TODO
        return retcode

    def post_process(self, retcode):
        # TODO
        return retcode

    def on_aggregated_data(self, data, stats):
        if self.test_start_time is None:
            self.test_start_time = stats['ts']

        self.api_client.send_job_record(
            self.job_id,
            data,
            stats,
            stats['ts'] - self.test_start_time,
        )
