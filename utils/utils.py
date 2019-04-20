
from datetime import datetime,date


def json_serial(obj):
    if isinstance(obj, (datetime,date)):
        return obj.isoformat()
    raise TypeError("Type {}s not serializable".format(obj))