# SPDX-License-Identifier: Apache-2.0
"""R62-FIX2: OFF startup semantics and STOP only when software observer active."""
import pathlib,unittest,subprocess,json,tempfile,importlib.util
R=pathlib.Path(__file__).resolve().parents[1]
JS=(R/'static/r55.js').read_text(); HTML=(R/'static/index.html').read_text();CSS=(R/'static/r55.css').read_text();APP=(R/'static/app.js').read_text()
class IdleNoEngineClaims(unittest.TestCase):
 def test_01_default_hidden_stop(self):self.assertRegex(HTML,r'id="r55-software-stop"[^>]*hidden disabled')
 def test_02_no_stop_at_idle(self):self.assertIn("el('r55-software-stop').hidden=!hasActiveObserver",JS)
 def test_03_selected_and_running_only(self):self.assertIn("monitoring&&value.selected===true",JS)
 def test_04_stop_unhides(self):self.assertIn("el('r55-software-stop').disabled=!hasActiveObserver",JS)
 def test_05_idle_note(self):self.assertIn('id="r55-idle-note"',HTML);self.assertIn("value.monitor_state!=='IDLE'",JS)
 def test_06_idle_no_engine_claim(self):self.assertIn("Aucun générateur acoustique ou EM n’a démarré",JS)
 def test_07_no_engine_stop_label(self):self.assertNotIn('Arrêter le moteur, la surveillance et la route',JS)
 def test_08_new_label(self):self.assertIn('Arrêter la surveillance et libérer la route',JS)
 def test_09_not_physical_start(self):self.assertIn('Aucun générateur physique ne peut démarrer',HTML)
 def test_10_no_python_change(self):self.assertNotIn('AudioQueueStart',(R/'app.py').read_text())
 def test_11_native_main_guard(self):self.assertIn('output_hard_denied.c',(R/'app.py').read_text())
 def test_12_monotonic_idle_contract(self):self.assertIn('if self._monitor_shutdown.is_set() or self.route is None:',(R/'app.py').read_text())
 def test_13_role_status(self):self.assertIn('class="r55-idle-note" role="status"',HTML)
 def test_14_idempotent_stop_guard(self):self.assertIn("if(data.software_stop!=='EXECUTED_NATIVE_FM_STOP'",JS)
 def test_15_ten_languages(self):
  for lang in ('fr','en','de','ar','es','pt','hr','it','zh','ko'):self.assertIn("  "+lang+":",JS)
 def test_16_button_hidden_style(self):self.assertIn('.r55-stop-btn[hidden]',CSS)
 def test_17_idle_note_hidden_style(self):self.assertIn('.r55-idle-note[hidden]',CSS)
 def test_18_relaunch_version(self):self.assertIn('v0.8.1',HTML)
 def test_19_no_generator_running_claim(self):self.assertIn('aucun générateur démarré',APP)
 def test_20_no_engine_in_stop_event(self):self.assertIn('Surveillance arrêtée · route libérée',JS)
 def test_21_readonly_os_monitor_status(self):self.assertIn('GET', (R/'app.py').read_text())
 def test_22_status_source_check(self):self.assertIn('monitor_state',JS)
 def test_23_js_syntax(self):
  for file in ('r55.js','cleanup.js','app.js'):
   p=subprocess.run(['node','--check',str(R/'static'/file)],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr)
