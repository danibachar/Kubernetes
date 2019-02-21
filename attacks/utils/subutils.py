import logging

class Base(object):
    def __init__(self):
        # Logger
        self.logger = logging.getLogger(__name__)


def safe_open(file_name_with_dierctory: str, permision="wb+"):
    if not os.path.exists(os.path.dirname(file_name_with_dierctory)):
        try:
            os.makedirs(os.path.dirname(file_name_with_dierctory))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    return open(file_name_with_dierctory, permision)