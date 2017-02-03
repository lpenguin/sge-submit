# coding=utf-8
import sys
import select


def has_stdin():
    """
    rtype: bool
    """
    return bool(select.select([sys.stdin,],[],[],0.0)[0])


def iter_stdin():
    """
    :rtype: list[str]
    """
    return filter(bool, map(str.strip, sys.stdin))


def progress_bar (iteration, total, running, prefix ='', suffix ='', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))

    filledLength = int(round(barLength * iteration / float(total)))
    unfilled_length = barLength - filledLength
    running_length = int(round(barLength * running / float(total)))
    running_length = min(unfilled_length, running_length)

    rest_length = unfilled_length - running_length

    bar = u'█' * filledLength + '+' * running_length + '-' * rest_length
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()