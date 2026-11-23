# SPDX-License-Identifier: Apache-2.0
"""GEN-R59 UI BUTTONS FIX1 — scoping, styles, UX and unchanged native hooks."""
from html.parser import HTMLParser
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT/'static/index.html').read_text(encoding='utf-8')
CSS = (ROOT/'static/cleanup.css').read_text(encoding='utf-8')
APP = (ROOT/'app.py').read_text(encoding='utf-8')

class ReadHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.buttons = {}; self.all_ids = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get('id'): self.all_ids.append(d['id'])
        if tag == 'button' and d.get('id') in ('r54-bind', 'r54-refresh', 'r54-clear'):
            self.buttons[d['id']] = d

page = ReadHTML(); page.feed(HTML)

class CoreAudioButtons(unittest.TestCase):
    def test_01_three_action_buttons_maintained(self):
        self.assertEqual(set(page.buttons), {'r54-bind','r54-refresh','r54-clear'})
    def test_02_no_duplicate_ids(self):
        self.assertEqual(len(page.all_ids), len(set(page.all_ids)))
    def test_03_primary_selection(self):
        self.assertIn('fm-device-action--primary', page.buttons['r54-bind']['class'])
    def test_04_secondary_refresh(self):
        self.assertIn('fm-device-action--refresh', page.buttons['r54-refresh']['class'])
    def test_05_subtle_clear(self):
        self.assertIn('fm-device-action--clear', page.buttons['r54-clear']['class'])
    def test_06_correct_business_order(self):
        self.assertLess(HTML.index('id="r54-bind"'), HTML.index('id="r54-refresh"'))
        self.assertLess(HTML.index('id="r54-refresh"'), HTML.index('id="r54-clear"'))
    def test_07_button_semantics(self):
        for b in page.buttons.values():
            self.assertEqual(b.get('type'), 'button')
            self.assertIn('r54-route-state',b.get('aria-controls', ''))
            self.assertIn('fm-device-action', b['class'])
    def test_08_existing_i18n_labels(self):
        for x in ('r54-bind-label','r54-refresh-label','r54-clear-label'):
            self.assertIn('id="'+x+'"', HTML)
            self.assertIn(x, (ROOT/'static/r54.js').read_text(encoding='utf-8'))
    def test_09_no_inline_event_handlers(self):
        for v in page.buttons.values():
            self.assertFalse(any(k.startswith('on') for k in v))
    def test_10_patch_is_last_stylesheet(self):
        self.assertGreater(HTML.index('href="/cleanup.css"'), HTML.index('href="/r54.css"'))
    def test_11_theme_uses_valid_vars(self):
        for key in ('--text', '--blue', '--page', '--border', '--muted'):
            self.assertIn('var('+key+')', CSS)
        section=CSS.split('/* GEN-R59 UI BUTTONS FIX1')[1]
        for bad in ('var(--txt)', 'var(--window)', 'var(--edge)'):
            self.assertNotIn(bad,section)
    def test_12_native_button_style_explicit(self):
        for s in ('-webkit-appearance:none','min-height:45px','border-radius:12px',
                  'font-family:inherit','font-weight:770','outline-offset:3px'):
            self.assertIn(s,CSS)
    def test_13_button_hover_and_focus(self):
        for s in ('.fm-device-action:hover:not(:disabled)',
                  '.fm-device-action:focus-visible',
                  '.fm-device-action:disabled',
                  '.fm-device-action:active:not(:disabled)'):
            self.assertIn(s,CSS)
    def test_14_small_screen_grid(self):
        self.assertIn('@media(max-width:420px)',CSS)
        self.assertIn('grid-template-columns:minmax(0,1fr)',CSS)
    def test_15_rtl_and_reduced_motion(self):
        self.assertIn('html[dir="rtl"] .app-shell .r54-route-actions',CSS)
        self.assertIn('@media(prefers-reduced-motion:reduce)',CSS)
    def test_16_js_r54_unchanged(self):
        self.assertIn('A detected device must not be mistaken for a confirmed route', (ROOT/'static/r54.js').read_text())
    def test_17_js_r59_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT/'static/r59.js').read_bytes()).hexdigest(),
                         '23b8e1d65d32b8ad744c3490878bbcc235c4973429f6df96767ad184edb45657')
    def test_18_no_new_physical_output_path(self):
        self.assertIn('GEN_R59_NATIVE_SESSION=COMPILED_NO_EMISSION',APP)
        self.assertIn('output_hard_denied.c',APP)
        self.assertNotIn('/api/audio/play',HTML)
    def test_19_new_version_and_original_routes(self):
        self.assertIn('v0.8.1',HTML)
        self.assertIn('id="r54-select"',HTML)
        self.assertIn('id="r55-software-stop"',HTML)
        self.assertIn('id="r59-bind"',HTML)
    def test_20_source_guardian_unchanged(self):
        self.assertTrue((ROOT/'native/output_hard_denied.c').is_file())
        self.assertIn('return -1', (ROOT/'native/output_hard_denied.c').read_text())

if __name__ == '__main__': unittest.main()
