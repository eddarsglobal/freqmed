#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read exact original CoreAudio candidate C blobs from local Git or from pinned GitHub Git blobs.

Github fallback requires explicit FREQMED_R58_FETCH_PINNED_GITHUB=YES and `gh api`;
never downloads an unverified ref, mutates user Git, or authorizes hardware output.
"""
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
PINS=json.loads((ROOT/'SOURCE_PINS_R58.json').read_text(encoding='utf8'))['files']
MAX_BLOB_BYTES=131072
GITHUB_REPO='eddarsglobal/freqmed'


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()


def valid_pins():
    if len(PINS)!=5 or any(not re.fullmatch(r'[a-z][a-z0-9_]*\.(?:c|h)',name) or
                                not re.fullmatch(r'[0-9a-f]{40}',sha) for name,sha in PINS.items()):
        raise RuntimeError('R58_PIN_MANIFEST_INVALID')


def local_candidates():
    home=Path.home()
    env=os.environ.get('FREQMED_SOURCE_REPO','').strip()
    repos=[Path(env).expanduser()] if env else []
    repos += [home/'Documents/App_py/freqmed',home/'Documents/App_py/FreqMed/Github',
              home/'Documents/App_py/FREQMED/Github',home/'Documents/App_py/freqmed/Github']
    return [p for p in dict.fromkeys(repos) if p.is_dir() and not p.is_symlink()]


def local_sources():
    for repo in local_candidates():
        extracted={}
        for name,blob in PINS.items():
            raw=None
            try:
                proc=subprocess.run(['git','-C',str(repo),'cat-file','blob',blob],
                                    stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                    timeout=8,check=False)
                if proc.returncode==0 and len(proc.stdout)<=MAX_BLOB_BYTES and git_blob(proc.stdout)==blob:
                    raw=proc.stdout
            except (OSError, subprocess.TimeoutExpired):
                pass
            if raw is None:
                candidate=repo/'generator'/'src'/name
                if candidate.is_file() and not candidate.is_symlink():
                    data=candidate.read_bytes()
                    if len(data)<=MAX_BLOB_BYTES and git_blob(data)==blob:
                        raw=data
            if raw is None:
                break
            extracted[name]=raw
        if set(extracted)==set(PINS):
            return extracted
    return None


def parse_github_blob(payload, expected_sha):
    if len(payload)>MAX_BLOB_BYTES*3:
        raise RuntimeError('R58_GITHUB_RESPONSE_EXCEEDS_LIMIT')
    try:
        document=json.loads(payload)
        if not isinstance(document,dict) or document.get('sha')!=expected_sha or document.get('encoding')!='base64':
            raise RuntimeError('R58_GITHUB_BLOB_METADATA_MISMATCH')
        encoded=document.get('content')
        if not isinstance(encoded,str):
            raise RuntimeError('R58_GITHUB_BASE64_MISSING')
        encoded=''.join(encoded.split())
        raw=base64.b64decode(encoded,validate=True)
        if len(raw)>MAX_BLOB_BYTES or document.get('size')!=len(raw) or git_blob(raw)!=expected_sha:
            raise RuntimeError('R58_GITHUB_BLOB_SHA_OR_SIZE_MISMATCH')
        return raw
    except (ValueError, UnicodeError, binascii.Error, TypeError):
        raise RuntimeError('R58_GITHUB_BLOB_DECODE_INVALID') from None


def github_pinned_sources():
    if os.environ.get('FREQMED_R58_FETCH_PINNED_GITHUB','').strip()!='YES':
        raise RuntimeError('R58_PINNED_SOURCES_NOT_LOCAL_GITHUB_READONLY_OPT_IN_REQUIRED')
    gh=shutil.which('gh')
    if not gh:
        raise RuntimeError('R58_GITHUB_CLI_GH_NOT_INSTALLED')
    fetched={}
    for name,sha in PINS.items():
        endpoint='repos/'+GITHUB_REPO+'/git/blobs/'+sha
        try:
            result=subprocess.run([gh,'api','--method','GET',endpoint],
                                  stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                  timeout=30,check=False)
        except (OSError, subprocess.TimeoutExpired):
            raise RuntimeError('R58_GITHUB_READONLY_REQUEST_FAILED') from None
        if result.returncode!=0:
            raise RuntimeError('R58_GITHUB_READONLY_REQUEST_FAILED_CHECK_GH_AUTH_OR_CONNECTIVITY')
        fetched[name]=parse_github_blob(result.stdout,sha)
    return fetched


def extract_pinned(dest):
    valid_pins()
    dest=Path(dest)
    if dest.exists() and (dest.is_symlink() or any(dest.iterdir())):
        raise RuntimeError('CANDIDATE_DESTINATION_MUST_BE_EMPTY')
    sources=local_sources()
    origin='LOCAL_GIT_SHA_PINNED'
    if sources is None:
        sources=github_pinned_sources()
        origin='GITHUB_READONLY_SHA_PINNED'
    # All 5 blobs have been verified before writing any source.
    if set(sources)!=set(PINS) or any(git_blob(sources[n])!=s for n,s in PINS.items()):
        raise RuntimeError('R58_PINNED_SOURCE_VERIFICATION_FAILED')
    dest.mkdir(mode=0o700,parents=True,exist_ok=True)
    for name,raw in sources.items():
        target=dest/name
        with target.open('xb') as handle: handle.write(raw)
        target.chmod(0o600)
    return {'source_origin':origin,'verified_blobs':len(sources),'source_files':list(sources)}


if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('USAGE: candidate_source_r58.py EMPTY_DEST_DIR')
    print(json.dumps(extract_pinned(Path(sys.argv[1])),ensure_ascii=False))
