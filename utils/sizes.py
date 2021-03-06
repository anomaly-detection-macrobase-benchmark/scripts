units = ['', 'K', 'M']


def format_size(num):
    for unit in units[:-1]:
        if abs(num) < 1000:
            return "%d%s" % (num, unit)
        num /= 1000
    return "%d%s" % (num, units[-1])


def parse_size(s):
    s = s.upper()
    unit_num = '000'
    for unit in units[1:]:
        s = s.replace(unit, unit_num)
        unit_num += '000'
    return int(s)
