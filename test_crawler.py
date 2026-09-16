import argparse
from datetime import date

from crawler import days_arg, is_match

cut = date(2026, 9, 8)
assert is_match({'severity': 'Critical', 'published': '2026-09-08'}, cut)  # cutoff day inclusive
assert is_match({'severity': 'High', 'published': '2026-09-15'}, cut)
assert not is_match({'severity': 'Medium', 'published': '2026-09-10'}, cut)
assert not is_match({'severity': 'Critical', 'published': '2026-09-07'}, cut)

assert days_arg('1') == 1 and days_arg('90') == 90
for bad in ('0', '91', '-3'):
    try:
        days_arg(bad)
        raise AssertionError(f'{bad} should be rejected')
    except argparse.ArgumentTypeError:
        pass
print('ok')
