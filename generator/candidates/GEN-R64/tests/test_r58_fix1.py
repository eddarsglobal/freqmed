# SPDX-License-Identifier: Apache-2.0
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r58_fix1_candidate_sources',ROOT/'candidate_source_r58.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class R58Fix1SourceRecovery(unittest.TestCase):
    def test_01_pins_exactly_five(self):
        self.assertEqual(len(m.PINS),5)
        m.valid_pins()
    def test_02_git_blob_contract(self):
        self.assertEqual(m.git_blob(b'example'),'96236f8158b12701d5e75c14fb876c4a0f31b963')
    def test_03_github_fallback_explicit_opt_in(self):
        with patch.dict(os.environ,{'FREQMED_R58_FETCH_PINNED_GITHUB':'NO'}):
            with self.assertRaisesRegex(RuntimeError,'OPT_IN_REQUIRED'):
                m.github_pinned_sources()
    def test_04_no_network_by_default(self):
        with patch.object(m,'local_sources',return_value=None):
            with patch.dict(os.environ,{'FREQMED_R58_FETCH_PINNED_GITHUB':'NO'}):
                with tempfile.TemporaryDirectory() as directory:
                    with self.assertRaisesRegex(RuntimeError,'OPT_IN_REQUIRED'):
                        m.extract_pinned(Path(directory)/'source')
    def test_05_exact_github_json_encoding_validated(self):
        data=b'/* FOSS source provenance validator */'
        sha=m.git_blob(data)
        payload=json.dumps({'sha':sha,'encoding':'base64','size':len(data),
                            'content':base64.b64encode(data).decode()}).encode()
        self.assertEqual(m.parse_github_blob(payload,sha),data)
    def test_06_wrong_git_sha_refused(self):
        data=b'/* FOSS source provenance validator */'
        sha=m.git_blob(data)
        payload=json.dumps({'sha':'0'*40,'encoding':'base64','size':len(data),
                            'content':base64.b64encode(data).decode()}).encode()
        with self.assertRaisesRegex(RuntimeError,'METADATA_MISMATCH'):
            m.parse_github_blob(payload,sha)
    def test_07_modified_source_refused(self):
        good=b'original'; corrupt=b'corrupted'
        sha=m.git_blob(good)
        payload=json.dumps({'sha':sha,'encoding':'base64','size':len(corrupt),
                            'content':base64.b64encode(corrupt).decode()}).encode()
        with self.assertRaisesRegex(RuntimeError,'SHA_OR_SIZE_MISMATCH'):
            m.parse_github_blob(payload,sha)
    def test_08_bad_base64_refused(self):
        sha=m.git_blob(b'data')
        payload=json.dumps({'sha':sha,'encoding':'base64','size':4,'content':'not:base64'}).encode()
        with self.assertRaisesRegex(RuntimeError,'DECODE_INVALID'):
            m.parse_github_blob(payload,sha)
    def test_09_wrong_size_refused(self):
        data=b'data'; sha=m.git_blob(data)
        payload=json.dumps({'sha':sha,'encoding':'base64','size':4000,
                            'content':base64.b64encode(data).decode()}).encode()
        with self.assertRaisesRegex(RuntimeError,'SHA_OR_SIZE_MISMATCH'):
            m.parse_github_blob(payload,sha)
    def test_10_non_base64_refused(self):
        sha=m.git_blob(b'data')
        with self.assertRaisesRegex(RuntimeError,'METADATA_MISMATCH'):
            m.parse_github_blob(json.dumps({'sha':sha,'encoding':'utf-8','size':4,'content':'data'}).encode(),sha)
    def test_11_invalid_pin_name_refused(self):
        with patch.object(m,'PINS',{'../evil.c':'0'*40}):
            with self.assertRaisesRegex(RuntimeError,'PIN_MANIFEST_INVALID'):
                m.valid_pins()
    def test_12_no_gh_executable_refused(self):
        with patch.dict(os.environ,{'FREQMED_R58_FETCH_PINNED_GITHUB':'YES'}):
            with patch.object(m.shutil,'which',return_value=None):
                with self.assertRaisesRegex(RuntimeError,'GH_NOT_INSTALLED'):
                    m.github_pinned_sources()
    def test_13_reads_exact_sha_pinned_gh_endpoint(self):
        data=b'/* Original source bytes already validated by Git SHA */'
        sha=m.git_blob(data)
        payload=json.dumps({'sha':sha,'encoding':'base64','size':len(data),
                            'content':base64.b64encode(data).decode()}).encode()
        with patch.object(m,'PINS',{'acoustic_macos.c':sha}):
            with patch.dict(os.environ,{'FREQMED_R58_FETCH_PINNED_GITHUB':'YES'}):
                with patch.object(m.shutil,'which',return_value='/usr/local/bin/gh'):
                    with patch.object(m.subprocess,'run',return_value=Mock(returncode=0,stdout=payload)) as runner:
                        self.assertEqual(m.github_pinned_sources()['acoustic_macos.c'],data)
                        argv=runner.call_args.args[0]
                        self.assertEqual(argv,[ '/usr/local/bin/gh','api','--method','GET',
                          'repos/eddarsglobal/freqmed/git/blobs/'+sha ])
    def test_14_failed_github_no_write(self):
        with patch.dict(os.environ,{'FREQMED_R58_FETCH_PINNED_GITHUB':'YES'}):
            with patch.object(m,'local_sources',return_value=None):
                with patch.object(m.shutil,'which',return_value='/usr/local/bin/gh'):
                    with patch.object(m.subprocess,'run',return_value=Mock(returncode=1,stdout=b'')):
                        with tempfile.TemporaryDirectory() as directory:
                            dest=Path(directory)/'candidate'
                            with self.assertRaisesRegex(RuntimeError,'REQUEST_FAILED'):
                                m.extract_pinned(dest)
                            self.assertFalse(dest.exists())
    def test_15_full_5_source_landing_is_atomic_before_write(self):
        blobs={n:('/* '+n+' */\n').encode() for n in m.PINS}
        pins={n:m.git_blob(raw) for n,raw in blobs.items()}
        with patch.object(m,'PINS',pins):
            with patch.object(m,'local_sources',return_value=dict(blobs)):
                with tempfile.TemporaryDirectory() as directory:
                    dest=Path(directory)/'candidate'
                    evidence=m.extract_pinned(dest)
                    self.assertEqual(evidence['verified_blobs'],5)
                    self.assertEqual(evidence['source_origin'],'LOCAL_GIT_SHA_PINNED')
                    self.assertEqual({p.name:p.read_bytes() for p in dest.iterdir()},blobs)
    def test_16_preexisting_dest_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)
            (dest/'existing').write_text('keep')
            with self.assertRaisesRegex(RuntimeError,'CANDIDATE_DESTINATION_MUST_BE_EMPTY'):
                m.extract_pinned(dest)
    def test_17_no_physical_playback_callable_in_helper(self):
        s=(ROOT/'candidate_source_r58.py').read_text()
        self.assertNotIn('AudioQueueStart',s)
        self.assertNotIn('fm_acoustic_physical_output(',s)
    def test_18_main_physical_denial_unchanged(self):
        self.assertIn('output_hard_denied.c',(ROOT/'app.py').read_text())
    def test_19_original_emitter_not_shipped(self):
        self.assertFalse((ROOT/'native/acoustic_macos.c').exists())
    def test_20_no_git_write_actions_in_source_helper(self):
        s=(ROOT/'candidate_source_r58.py').read_text()
        self.assertNotIn("'fetch'",s)
        self.assertNotIn("'checkout'",s)
        self.assertNotIn("'clone'",s)
