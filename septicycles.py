from math import floor
from datetime import datetime, timedelta
from time import mktime

EPOCH = 1389150000000
CYCLE_LENGTH = 630000000
CHECKPOINT_LENGTH = 18000


def current_cycle():
    present = datetime.now()
    tt = datetime.timetuple(present)
    now = mktime(tt) * 1000
    cycle = floor((now - EPOCH) / CYCLE_LENGTH)
    start = datetime.fromtimestamp(CHECKPOINT_LENGTH + ((EPOCH + (cycle * CYCLE_LENGTH)) / 1000))

    checkpoints = []
    for i in range(0, 35):
        next = (start > present) and (present + timedelta(seconds=CHECKPOINT_LENGTH)) > start
        cp = {
            'date': start.strftime('%a %d %b'),
            'time': start.strftime('%I:%M%p'),
            'next': next,
            'past': (start < present)
        }
        checkpoints.append(cp)
        start = start + timedelta(seconds=CHECKPOINT_LENGTH)
    return checkpoints


def next_checkpoint(cps):
    future = [cp for cp in cps if cp['past'] is False]
    return future[0]


def cycle_end(cps):
    return cps[-1]


def main():
    cps = current_cycle()
    n = next_checkpoint(cps)
    c = cycle_end(cps)
    "Next checkpoint is {} <b>{}</b>.\nThis cycle ends {} <b>{}</b>.".format(n['date'], n['time'], c['date'], c['time'])


if __name__ == "__main__":
    main()
