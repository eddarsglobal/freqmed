#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""BENCH-02: read-only acoustic binding; no stream or physical admission."""
import hashlib, json, math, pathlib, platform, re, subprocess, sys, tempfile

BASE = 'c5da76be8f33cd9e927772e6cc492745d180bebd'
EM = '0412c0fbe2b54298a3b1dd346c78d3b56dda0e63'
PINS = [(BASE,'generator/candidates/BENCH-01/mac_bench.c','1f488aafa231e33b6866285cc6dbd84e2651adb9'),
        (EM,'generator/candidates/GEN-EM-01/native/em_hardware_discovery.h','478c2c7bb624325946da39751fefc342fdf07188')]
ROUTES = {'BUILT_IN','USB','VIRTUAL','AGGREGATE','BLUETOOTH','OTHER','UNKNOWN'}

def fingerprint(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def parse(raw):
    pair={}
    for line in raw.splitlines():
        p=line.split('\t')
        if len(p)!=12 or p[0] not in ('I','O') or p[0] in pair or p[2] not in ROUTES:
            raise ValueError('ROW')
        ident,n=int(p[1]),int(p[3]); rate=float(p[4]); clock,alive,frames,latency,safety,running=map(int,p[5:11])
        if not (0<ident<=4294967295 and -1<=n<=256 and math.isfinite(rate) and 0<rate<=384000
                and -1<=clock<=4294967295 and alive in (-1,0,1) and running in (-1,0,1)
                and all(-1<=x<=4294967295 for x in (frames,latency,safety))
                and re.fullmatch(r'(?:[0-9a-f]{2}){1,1023}',p[11])):
            raise ValueError('VALUE')
        pair[p[0]]={'os_id':ident,'route':p[2],'channels':None if n<0 else n,'nominal_rate_hz':rate,
                    'identity_sha256':hashlib.sha256(bytes.fromhex(p[11])).hexdigest(),
                    'clock_domain':None if clock<0 else clock,'alive':None if alive<0 else bool(alive),
                    'buffer_frames':None if frames<0 else frames,'device_latency_frames':None if latency<0 else latency,
                    'safety_offset_frames':None if safety<0 else safety,'running_somewhere':None if running<0 else bool(running)}
    if set(pair)!={'I','O'}:raise ValueError('MISSING_SIDE')
    return pair

def assess(a,b):
    stable=a==b
    o,i=b['O'],b['I']
    eligible=stable and all(e['route'] in ('BUILT_IN','USB') and e['alive'] is True and
        e['running_somewhere'] is False and e['channels'] is not None and e['channels']>0 and
        e['buffer_frames'] is not None and e['buffer_frames']>0 and e['device_latency_frames'] is not None and
        e['safety_offset_frames'] is not None for e in (o,i))
    same_clock=bool(o['clock_domain'] and i['clock_domain'] and o['clock_domain']==i['clock_domain'])
    same_rate=o['nominal_rate_hz']==i['nominal_rate_hz']
    distinct=o['identity_sha256']!=i['identity_sha256'] and o['os_id']!=i['os_id']
    separate=stable and distinct and i['route']=='USB' and i['alive'] is True and bool(i['channels'])
    return {'schema':'freqmed.bench-02.v1','metadata_stable':stable,'configuration_sha256':fingerprint(b),
            'endpoints':b,'binding':'READONLY_PAIR_CANDIDATE' if eligible else 'NOT_READY_METADATA',
            'same_nominal_rate':same_rate,'same_nonzero_clock_reported':same_clock,'distinct_endpoint_ids':distinct,
            'separate_usb_input_candidate':separate,'stream_sync':'NOT_TESTED','roundtrip_latency':'NOT_MEASURED',
            'measurement_provenance':'NO_PHYSICAL_MEASUREMENT','independent_metrology':'NOT_VERIFIED',
            'calibration':'NOT_VERIFIED','uncertainty':'NOT_ESTIMATED','independent_stop':'NOT_VERIFIED',
            'physical_backend_available':False,'output_stream_opened':False,'microphone_stream_opened':False,
            'physical_output':'NOT_PERFORMED','physical_measurement':'NOT_PERFORMED','authorization':'NONE',
            'certification':'NOT_ISSUED','hardware_qualified':False,'verdict':'READONLY_PREPARATION_ONLY'}

def tests():
    # Software parser vectors, never exported as native observations.
    raw='O\t1\tBUILT_IN\t2\t44100\t5\t1\t256\t32\t8\t0\t6161\nI\t2\tBUILT_IN\t1\t44100\t5\t1\t256\t20\t4\t0\t6262\n'
    a=parse(raw); r=assess(a,a)
    def reject(s):
        try:parse(s)
        except ValueError:return True
        return False
    def alter(old,new):return parse(raw.replace(old,new,1))
    usb=alter('I\t2\tBUILT_IN','I\t2\tUSB'); unknown=alter('\t5\t1\t256','\t0\t1\t256')
    busy=alter('\t8\t0\t6161','\t8\t1\t6161'); latency=alter('\t32\t8','\t-1\t8')
    different=alter('I\t2\tBUILT_IN\t1\t44100','I\t2\tBUILT_IN\t1\t48000')
    checks={'pair':r['binding']=='READONLY_PAIR_CANDIDATE','stable':r['metadata_stable'],
      'shared_clock':r['same_nonzero_clock_reported'],'unknown_clock':not assess(unknown,unknown)['same_nonzero_clock_reported'],
      'nominal_rate':r['same_nominal_rate'],'rate_difference':not assess(different,different)['same_nominal_rate'],
      'integrated_not_independent':not r['separate_usb_input_candidate'],'usb_candidate_only':assess(usb,usb)['separate_usb_input_candidate'] and not assess(usb,usb)['hardware_qualified'],
      'unstable':assess(a,usb)['binding']=='NOT_READY_METADATA','busy':assess(busy,busy)['binding']=='NOT_READY_METADATA',
      'unknown_latency':assess(latency,latency)['binding']=='NOT_READY_METADATA','fingerprint_change':fingerprint(a)!=fingerprint(usb),
      'duplicate':reject(raw+raw),'nonfinite':reject(raw.replace('44100','nan')),'missing':reject(raw.splitlines()[0]),
      'bad_identity':reject(raw.replace('6161','zz')),'no_output':r['physical_backend_available'] is False and r['output_stream_opened'] is False and r['microphone_stream_opened'] is False,
      'no_authorization':r['authorization']=='NONE' and r['independent_metrology']=='NOT_VERIFIED'}
    print('BENCH02_SOFTWARE_CHECKS='+json.dumps(checks,sort_keys=True),flush=True)
    if not all(checks.values()):raise SystemExit('BENCH02_SOFTWARE_FAIL')
    print('BENCH02_SOFTWARE_PASS='+str(len(checks))+'/'+str(len(checks)),flush=True)

def native(repo):
    with tempfile.TemporaryDirectory(prefix='freqmed_bench02_') as t:
        w=pathlib.Path(t)
        for ref,path,pin in PINS:
            data=subprocess.check_output(['git','-C',str(repo),'show',ref+':'+path],timeout=30)
            if hashlib.sha1(('blob %d'%len(data)).encode()+b'\0'+data).hexdigest()!=pin:raise RuntimeError('PIN_MISMATCH '+path)
            if path.endswith('mac_bench.c'):
                s=data.decode(); marker='int main(void){'
                if s.count(marker)!=1:raise RuntimeError('PREFIX_BOUNDARY')
                (w/'bench01_prefix.inc').write_text(s.split(marker)[0],encoding='utf-8')
            else:(w/pathlib.Path(path).name).write_bytes(data)
        exe=w/'preflight'
        subprocess.run(['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I',str(w),str(pathlib.Path(__file__).resolve().parent/'mac_preflight.c'),'-framework','CoreAudio','-framework','CoreFoundation','-o',str(exe)],check=True,timeout=120)
        print('BENCH02_SOURCE_PINS=2/2 PASS',flush=True)
        return [parse(subprocess.check_output([str(exe)],text=True,timeout=20)) for _ in range(2)]

if __name__=='__main__':
    tests()
    if sys.argv[1:]==['--self-test']:sys.exit(0)
    if platform.system()!='Darwin' or len(sys.argv)!=2:raise SystemExit('USAGE_MAC: python3 -B preflight.py REPO')
    first,second=native(pathlib.Path(sys.argv[1]).resolve(strict=True))
    print('BENCH02_REPORT='+json.dumps(assess(first,second),sort_keys=True,allow_nan=False),flush=True)
