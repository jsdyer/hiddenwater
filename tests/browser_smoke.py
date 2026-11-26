"""CI checks real bundled data and project-subpath flows; external tiles are stubbed."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import re
import json, shutil, tempfile, threading
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    slug=json.loads((ROOT/'tool.json').read_text())['id']
    shots=ROOT/'browser-checks'; shots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        shutil.copytree(ROOT/'dist',Path(temp)/slug)
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=temp))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH")); page=browser.new_page(viewport={'width':1440,'height':1050})
                errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
                svg='<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect width="256" height="256" fill="#dce4d5"/></svg>'
                page.route('https://tile.openstreetmap.org/**',lambda r:r.fulfill(content_type='image/svg+xml',body=svg))
                wms=[]
                def imagery(route):
                    q=parse_qs(urlsplit(route.request.url).query)
                    assert q.get('layers')==['halifax'] and q.get('time') in [['1947-07-01T12:00:00Z'],['1977-07-01T12:00:00Z']]
                    wms.append(q); route.fulfill(content_type='image/svg+xml',body=svg)
                page.route('https://datacube.services.geo.ca/ows/aerial*',imagery)
                base=f'http://127.0.0.1:{server.server_port}/{slug}/'
                page.goto(base)
                if slug=='halifaxtimelens':
                    expect(page.locator('#status')).to_contain_text('Comparison ready')
                    assert {q['time'][0][:4] for q in wms}=={'1947','1977'}
                    page.locator('#reveal').fill('70')
                    assert '70%' in page.locator('#right-map').get_attribute('style')
                    page.locator('#right-year').select_option('streets')
                    expect(page.locator('#right-label')).to_have_text('Modern street map')
                    page.locator('[data-place="dartmouth"]').click()
                    expect(page.locator('#place-title')).to_have_text('Downtown Dartmouth')
                    page.locator('#share').click(); url=page.locator('#share-url').input_value()
                    assert 'right=streets' in url and 'split=70' in url
                    page.goto(url); expect(page.locator('#right-year')).to_have_value('streets')
                    expect(page.locator('#reveal')).to_have_value('70')
                    page.locator('#swap').click(); expect(page.locator('#left-year')).to_have_value('streets')
                elif slug=='hiddenwater':
                    case = page.locator('#crossing-1474')
                    stages = json.loads((ROOT / 'web/data/crossing.json').read_text())['stages']
                    habitat = stages['habitat']['HABCONF_VERIFIED_HABITAT_LEN']
                    cost = stages['completion']['REMEDIATION_COST']
                    if habitat is not None:
                        expect(case).to_contain_text(f'{habitat:,.0f} m')
                    expect(case).to_contain_text('1,000 m of high-value habitat')
                    expect(case.locator('.case-cost')).to_have_text(f'${cost:,.0f}' if cost is not None else 'Unreported')
                    expect(case.locator('details')).to_have_count(4)
                    case.get_by_text('Completed work', exact=False).first.click()
                    expect(case.locator('details[open] a')).to_have_attribute('href', re.compile('MapServer/1/query'))
                    expect(case.get_by_text('Read the Chilliwack River coho', exact=False)).to_have_attribute('href', 'https://coolcode.ca/salmonlines/series/46982-62/')
                    page.locator('.result').first.wait_for()
                    page.locator('#in-view').uncheck(); page.locator('#query').fill('Yorkson')
                    page.locator('#filters button[type="submit"]').click()
                    page.locator('.result').first.wait_for(); assert 'Yorkson' in page.locator('.result').first.inner_text()
                    page.locator('.result').first.click(); page.locator('#detail h2').wait_for()
                    expect(page.get_by_role('link', name='Explore this name in BC Place Names')).to_have_attribute('href', 'https://coolcode.ca/bcplacenames/#name=25298')
                    expect(page.get_by_role('link',name='Read the DFO coho estimates')).to_have_attribute('href', 'https://coolcode.ca/salmonlines/series/47959-26/')
                    page.get_by_role('button',name='Share this segment').click()
                    url=page.locator('#share-url').input_value(); assert '#record=' in url
                    with page.expect_download() as info:page.locator('#geojson').click()
                    data=json.loads(Path(info.value.path()).read_text()); assert data['features'] and data['sources']
                    page.goto(url); page.locator('#detail h2').wait_for()
                    snapshot = json.loads((ROOT / 'dist/data/water.json').read_text())
                    yorkson = [r for r in snapshot['features'] if r['properties']['name'] == 'Yorkson Creek' and r['properties']['kind'] != 'Culvert']
                    fragments = ['waterway=Yorkson+Creek']
                    previous_id = 'channels:9c7edd00-c189-44a7-a478-6b6c93f79ddf'
                    if not any(r['properties']['id'] == previous_id for r in snapshot['features']):
                        fragments.append('record=' + previous_id)
                    for fragment in fragments:
                        page.goto(base + '#' + fragment)
                        expect(page.locator('#map-area')).to_have_text('Yorkson Creek')
                        expect(page.locator('#count')).to_have_text(str(len(yorkson)))
                        expect(page.locator('#detail')).to_contain_text('mapped reach')
                        expect(page.locator('#detail a')).to_have_attribute('href', 'https://coolcode.ca/salmonlines/series/47959-26/')
                    page.locator('.result').first.click()
                    expect(page.get_by_role('link',name='Read the DFO coho estimates')).to_have_attribute('href', 'https://coolcode.ca/salmonlines/series/47959-26/')
                    page.locator('#query').fill('nonexistentwaterwayzzzz'); page.locator('#filters button[type="submit"]').click()
                    expect(page.locator('#status')).to_contain_text('No matching'); assert page.locator('#csv').is_disabled()
                    page.locator('[data-place="city"]').click(); page.locator('.result').first.wait_for()
                else:
                    page.locator('.result').first.wait_for(); expect(page.locator('#count')).to_have_text(f"{len(json.loads((ROOT/'web/data/applications.json').read_text())['records']):,}")
                    page.locator('#changed').check(); assert int(page.locator('#count').inner_text().replace(',','')) <= len(json.loads((ROOT/'web/data/applications.json').read_text())['records'])
                    page.locator('#city-preset').click(); page.locator('.result').first.wait_for()
                    assert '0 Township' in page.locator('#map-caption').inner_text()
                    page.locator('.result').first.click(); page.locator('#detail h2').wait_for()
                    page.get_by_role('button',name='☆ Save application',exact=True).click()
                    page.locator('#saved').check(); expect(page.locator('.result')).to_have_count(1)
                    page.get_by_role('button',name='Share',exact=True).click(); url=page.locator('#share-url').input_value()
                    page.goto(url); page.get_by_role('button',name='★ Remove from saved',exact=True).wait_for()
                    with page.expect_download() as info:page.locator('#csv').click()
                    assert 'snapshot_retrieved' in Path(info.value.path()).read_text()
                    page.locator('#query').fill('nonexistentprojectzzzz'); page.locator('#filters button[type="submit"]').click()
                    expect(page.locator('#status')).to_contain_text('No matching')
                    page.locator('#willoughby').click(); page.locator('.result').first.wait_for()
                page.screenshot(path=str(shots/'desktop.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844})
                page.goto(base)
                expect(page.locator('#map-area')).to_have_text('Willoughby waterways')
                expect(page.locator('[data-place="willoughby"]')).to_have_attribute('aria-pressed', 'true')
                assert 0 <= page.locator('#map').bounding_box()['y'] < 844
                assert page.locator('#map').bounding_box()['y'] < page.locator('#filters').bounding_box()['y']
                page.locator('[data-place="fort"]').click()
                expect(page.locator('#map-area')).to_have_text('Fort Langley waterways')
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile page overflows horizontally'
                page.screenshot(path=str(shots/'mobile.png'),full_page=True)
                if slug!='halifaxtimelens':
                    page.route('**/data/*.json',lambda r:r.fulfill(status=503,body='Unavailable'))
                    page.reload(); expect(page.locator('#status')).to_contain_text('could not load')
                assert not errors, errors
                browser.close()
            print('Browser flows, source links, exports, saved/deep-link state, failure handling and mobile layout passed')
        finally:server.shutdown()
if __name__=='__main__': main()
