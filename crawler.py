"""Crawl Check Point security advisories (Critical/High) published within the last N days."""
import argparse
import csv
import random
import re
import sys
import time
from datetime import date, timedelta

from DrissionPage import ChromiumOptions, ChromiumPage

URL = 'https://support.checkpoint.com/security-advisories'
SEVERITIES = {'Critical', 'High'}
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36')


def log(msg):
    """Progress goes to stderr so stdout keeps only the results."""
    print(msg, file=sys.stderr, flush=True)


def human_pause(lo=1.0, hi=2.5):
    time.sleep(random.uniform(lo, hi))


def make_page(headless):
    co = (ChromiumOptions()
          .headless(headless)
          .auto_port()
          .set_user_agent(UA)  # headless UA contains "HeadlessChrome", replace it
          .set_argument('--window-size=1920,1080')  # narrow viewport renders cards, not a table
          .set_argument('--disable-blink-features=AutomationControlled')
          .set_argument('--lang=en-US')
          .set_argument('--no-sandbox'))
    page = ChromiumPage(co)
    page.run_cdp('Page.addScriptToEvaluateOnNewDocument',
                 source="Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
    return page


def parse_rows(page):
    """Return (tr element, record) for every data row on the current table page."""
    rows = []
    for tr in page.ele('tag:table', timeout=20).eles('xpath:./tbody/tr'):
        tds = tr.eles('tag:td')
        if len(tds) < 6:  # expanded "related products" rows
            continue
        link = tds[2].ele('tag:a')
        m = re.match(r'(CVE-\d{4}-\d+)\s*:\s*(.*)', link.text, re.S)
        rows.append((tr, {
            'cve': m.group(1) if m else '',
            'severity': tds[1].text.strip(),
            'summary': m.group(2).strip() if m else link.text.strip(),
            'cvss': tds[3].text.strip(),
            'published': tds[4].text.strip(),
            'updated': tds[5].text.strip(),
            'link': link.attr('href'),
        }))
    return rows


def is_match(r, cutoff):
    return r['severity'] in SEVERITIES and date.fromisoformat(r['published']) >= cutoff


def crawl(days, headless=True, shot=None, max_pages=50):
    cutoff = date.today() - timedelta(days=days)
    log(f'Opening browser (headless={headless}) ...')
    page = make_page(headless)
    results = []
    try:
        for attempt in range(3):
            log(f'Loading {URL} (attempt {attempt + 1}/3) ...')
            page.get(URL)
            if page.ele('tag:table', timeout=20):
                break
            human_pause(3 * (attempt + 1), 6 * (attempt + 1))  # backoff before retry
        else:
            raise RuntimeError('advisory table not found (blocked or layout changed)')

        for n in range(1, max_pages + 1):
            rows = parse_rows(page)
            if not rows:
                break
            hits = [(tr, r) for tr, r in rows if is_match(r, cutoff)]
            results += [r for _, r in hits]
            log(f'Page {n}: {len(rows)} rows ({rows[-1][1]["published"]}~{rows[0][1]["published"]}), '
                f'{len(hits)} match(es), {len(results)} total')
            if shot and (hits or n == 1):
                for tr, _ in hits:
                    tr.run_js('this.style.outline="3px solid red";this.style.background="#fff3a0"')
                page.get_screenshot(path=f'{shot}_p{n}.png', full_page=True)
            # ponytail: relies on the site's default newest-first order to stop early
            if date.fromisoformat(rows[-1][1]['published']) < cutoff:
                break
            nxt = page.ele('tag:button@@text():Next', timeout=5)
            if not nxt or nxt.attr('disabled') is not None:
                break
            human_pause()
            log('Next page ...')
            page.scroll.to_see(nxt)
            nxt.click()
            human_pause(0.8, 1.5)
    finally:
        log('Closing browser ...')
        page.quit()
    return cutoff, results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--days', type=int, choices=(3, 7), default=7,
                    help='published within N days of local date (default 7)')
    ap.add_argument('--out', default='checkpoint_cve.csv', help='CSV output path')
    ap.add_argument('--shot', help='screenshot prefix; saves <prefix>_p<N>.png with matched rows highlighted')
    ap.add_argument('--show', action='store_true', help='run with visible browser')
    a = ap.parse_args()

    log(f'Looking for Critical/High advisories published in the last {a.days} day(s) ...')
    cutoff, results = crawl(a.days, headless=not a.show, shot=a.shot)
    print(f'Local date {date.today()} | cutoff {cutoff} ({a.days} days) | {len(results)} match(es)')
    for r in results:
        print(f"{r['published']}  {r['severity']:<8} CVSS {r['cvss']:<4} {r['cve']:<16} {r['summary']}")
    with open(a.out, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['cve', 'severity', 'cvss', 'published', 'updated', 'summary', 'link'])
        w.writeheader()
        w.writerows(results)
    print(f'Saved {a.out}' + ('' if results else ' (no matching advisory, header only)'))


if __name__ == '__main__':
    sys.exit(main())
