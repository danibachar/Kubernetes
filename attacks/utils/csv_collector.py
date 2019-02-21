from .subutils import safe_open
import csv
import datetime

class CSVCollector(object):
    def __init__(self, args):
        super(CSVCollector, self).__init__()

    def __enter__(self):
        self.pub_batch = self.pub_topic.batch()
        self.count = 0
        self.total = 0


    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._commit()
        except Exception as e:
            self.logger.exception('Failed to commit batch')
        finally:
            self.logger.debug('Finished: committed a total of {} items to pubsub'.format(self.total))