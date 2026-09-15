from datetime import date

from crawler import is_match

cut = date(2026, 9, 8)
assert is_match({'severity': 'Critical', 'published': '2026-09-08'}, cut)  # cutoff day inclusive
assert is_match({'severity': 'High', 'published': '2026-09-15'}, cut)
assert not is_match({'severity': 'Medium', 'published': '2026-09-10'}, cut)
assert not is_match({'severity': 'Critical', 'published': '2026-09-07'}, cut)
print('ok')
