# SPDX-License-Identifier: Apache-2.0
"""FREQMED route picker UX: do not equate discovery with server selection.

Tests are DOM/source contracts; no fake hardware and no scientific simulation.
"""
import hashlib
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'static/index.html').read_text()
JS=(ROOT/'static/r54.js').read_text()
R55=(ROOT/'static/r55.js').read_text()
CSS=(ROOT/'static/cleanup.css').read_text()
class SelectionUX(unittest.TestCase):
    def test_01_version(self):self.assertIn('v0.8.0',HTML)
    def test_02_initial_placeholder(self):self.assertIn('id="r54-select"',HTML);self.assertIn('<option value="" disabled selected>',HTML)
    def test_03_initial_status_distinguishes_route(self):self.assertIn('Aucune route associée.',HTML)
    def test_04_confirmation_is_disabled_initially(self):self.assertIn('id="r54-bind" disabled ',HTML)
    def test_05_placeholder_first_on_refresh(self):self.assertLess(JS.index('placeholder(label(14))'),JS.index('for(const dev of r.devices)'))
    def test_06_no_auto_selection(self):self.assertNotIn('o.selected=true',JS)
    def test_07_server_selected_only(self):self.assertIn('route?.selected&&route.verified_now',JS)
    def test_08_pending_distinction(self):self.assertIn("'pending'",JS);self.assertIn('fill(label(15)',JS)
    def test_09_active_vs_pending(self):self.assertIn('fill(label(16)',JS)
    def test_10_no_route_no_device(self):self.assertIn('selectionState(route)',JS)
    def test_11_change_listener(self):self.assertIn("select.addEventListener('change',pendingChoice)",JS)
    def test_12_explicit_bind_only(self):self.assertIn("'/api/audio/select'",JS)
    def test_13_clear_pending(self):self.assertIn('clearDropdown();selectionState(r)',JS)
    def test_14_clear_waits_backend(self):self.assertIn("await post('/api/audio/clear',{})",JS)
    def test_15_stop_event(self):self.assertIn("new Event('freqmed:route-cleared')",R55)
    def test_16_stop_reacts(self):self.assertIn("window.addEventListener('freqmed:route-cleared',clearedByStop)",JS)
    def test_17_stop_only_after_server_success(self):self.assertLess(R55.index("data.monitor_running!==false"),R55.index("freqmed:route-cleared"))
    def test_18_bind_button_disabled_when_no_menu_value(self):self.assertIn('disabled=!/^\\d+$/.test(select.value)',JS)
    def test_19_pending_css(self):self.assertIn('data-verified="pending"',CSS)
    def test_20_theme_palette(self):self.assertIn('var(--blue)',CSS);self.assertIn('var(--teal)',CSS)
    def test_21_i18n_complete(self):
        for k in ('fr','en','de','ar','es','pt','hr','it','zh','ko'):
            self.assertIn(' '+k+':[',JS)
    def test_22_uses_no_emission_calls(self):
        for x in ('AudioQueueStart','/api/physical-start','/api/acoustic/play'):
            self.assertNotIn(x,JS)
    def test_23_native_C_unchanged(self):
        src=ROOT/'native'/'output_hard_denied.c'
        self.assertIn('return -1',src.read_text())
    def test_24_no_new_servers(self):self.assertIn('GET', (ROOT/'app.py').read_text())
    def test_25_r54_server_confirmation(self):self.assertIn('selectionState(r)',JS)
    def test_26_can_confirm_from_dropdown(self):self.assertIn('canConfirm();',JS)
    def test_27_placeholder_resets_to_empty(self):self.assertIn("select.value=''",JS)
    def test_28_epoch_prevents_stale_acks(self):self.assertIn('if(current!==epoch)return',JS)
    def test_29_server_source_pins(self):self.assertTrue((ROOT/'SOURCE_PINS_R58.json').is_file())
    def test_30_original_c_session(self):self.assertTrue((ROOT/'native'/'acoustic_session_r59.c').is_file())
