"""Structural and security tests only. No acoustic/EM scientific simulation."""
import pathlib
import json
import subprocess
import os
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

class SourceGuards(unittest.TestCase):
    def test_acoustic_entry_hard_denied(self):
        s = (SRC / "acoustic_macos.c").read_text()
        entry = s.split('int fm_acoustic_physical_output(', 1)[1]
        self.assertRegex(entry, r"return -1\s*;")
        self.assertNotIn('acoustic_output_impl(command)', entry)
    def test_em_hard_denied(self):
        s = (SRC / "em_backend.c").read_text()
        self.assertIn('return -1;', s)
        self.assertNotIn('open(', s)
        self.assertNotIn('write(', s)
    def test_no_auto_start(self):
        s = (SRC / "main.c").read_text()
        cli=s.split('int main(',1)[1]
        self.assertNotIn('fm_acoustic_physical_output(', cli)
        self.assertNotIn('fm_em_physical_output(', cli)
        self.assertNotIn('AudioQueueStart(', s)
    def test_source_build_no_network(self):
        for src in SRC.glob('*.c'):
            t=src.read_text()
            for term in ('curl_easy', 'socket(', 'connect(', 'NSURLSession', 'CFNetwork'):
                self.assertNotIn(term,t)
    def test_no_simulated_measurement_fixtures(self):
        for p in ROOT.rglob('*.csv'):
            self.fail(f"CSV measurement fixture forbidden: {p}")
    def test_user_visible_release_locked(self):
        self.assertIn('NOT_LINKED_HARD_DENIED', (SRC/'main.c').read_text())
        self.assertIn('BLOCKED_NO_QUALIFIED_EM_DEVICE', (SRC/'main.c').read_text())
    def test_doc_does_not_claim_output(self):
        t=(ROOT/'README_FR.md').read_text()
        self.assertIn('AUCUNE ÉMISSION PHYSIQUE',t)
    def test_macos_backend_uses_real_api(self):
        t=(SRC/'acoustic_macos.c').read_text()
        for s in ('AudioQueueNewOutput','AudioQueueStart','AudioQueueEnqueueBuffer','AudioQueueStop'):
            self.assertIn(s,t)
    def test_guardian_rejects_even_with_flags(self):
        t=(SRC/'generator_core.c').read_text()
        self.assertIn('g->state=FM_BLOCKED;',t)
        self.assertIn('R1_OUTPUT_HARD_LOCK_CERTIFICATION_REQUIRED',t)
    def test_no_gui_redesign(self):
        self.assertFalse((ROOT/'index.html').exists())
        self.assertFalse((ROOT/'assets').exists())

class ExecutableGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bin = os.environ.get('FREQMED_GEN_R1_BINARY','')
    def test_status_is_explicitly_non_emitting(self):
        if not self.bin: self.skipTest('Requires compiled native binary')
        r = subprocess.run([self.bin,'status'],text=True,capture_output=True,timeout=4)
        self.assertEqual(0,r.returncode)
        j=json.loads(r.stdout)
        self.assertEqual('NONE',j['physical_emission'])
        self.assertEqual('NOT_LINKED_HARD_DENIED',j['acoustic_output'])
        self.assertEqual('BLOCKED_NO_QUALIFIED_EM_DEVICE',j['electromagnetic_output'])
    def test_unknown_action_cannot_start_output(self):
        if not self.bin: self.skipTest('Requires compiled native binary')
        for action in ('emit','start','play','--emit','--run'):
            r=subprocess.run([self.bin,action],text=True,capture_output=True,timeout=4)
            self.assertNotEqual(0,r.returncode)
            self.assertIn('UNKNOWN_COMMAND_NO_OUTPUT',r.stderr)
    def test_selftest_detects_hard_denial(self):
        if not self.bin: self.skipTest('Requires compiled native binary')
        r=subprocess.run([self.bin,'selftest'],text=True,capture_output=True,timeout=4)
        self.assertEqual(0,r.returncode)
        self.assertIn('GUARDIAN=FAIL_CLOSED',r.stdout)
