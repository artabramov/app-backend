from decimal import Decimal

DECIMAL_PRECISION = 2


def app_decimal(value):
    parts = str(Decimal(value)).split('.')

    if len(parts) == 1:
        return Decimal(parts[0])

    else:
        parts[1] = parts[1][0:DECIMAL_PRECISION]
        return Decimal('%s.%s' % (parts[0], parts[1]))
