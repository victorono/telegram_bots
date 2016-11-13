
from datetime import datetime, timedelta
from time import mktime
from pytz import timezone


def checkpoints():

    time_zone = 'UTC'
    t0 = datetime.strptime('2014-07-09 11', '%Y-%m-%d %H').replace(tzinfo=timezone(time_zone))
    hours_per_cycle = 175

    t = datetime.utcnow()
    print(t)
    print(t0)

    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    cycles = seconds // (3600 * hours_per_cycle)
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    checkpoints = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))

    # for num, checkpoint in enumerate(checkpoints, start=1):
    #     print(checkpoint)
    #     # print('%2d %s' % (num, checkpoint))


if __name__ == '__main__':
    checkpoints()
