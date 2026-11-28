# SPDX-License-Identifier: Apache-2.0
"""Read-only descriptor admission; deliberately no activation capability."""
import math

REQUIRED = ('G2_HARDWARE_LIMITS_AND_INTERLOCKS', 'G3_NONBIOLOGICAL_BENCH_AUTHORIZATION',
            'INDEPENDENT_STOP', 'CALIBRATION_AND_METROLOGY', 'VERIFIED_RT_QUIESCENCE')

def parse(raw, parent):
    rows=raw.splitlines()
    if len(rows)<6 or len(rows)>66:raise ValueError('ROW_COUNT')
    pair=parent.parse('\n'.join(rows[:2]))
    formats={}
    for row in rows[2:]:
        p=row.split('\t')
        if len(p)!=13 or p[0]!='F' or p[1] not in ('I','O') or p[2] not in ('V','P'):raise ValueError('FORMAT_ROW')
        ident=int(p[3]);rate=float(p[4]);v=list(map(int,p[5:]))
        if not (0<ident<=4294967295 and math.isfinite(rate) and 0<rate<=384000 and
                all(0<=x<=4294967295 for x in v) and v[-1] in (0,1)):raise ValueError('FORMAT_VALUE')
        key=(p[1],ident,p[2])
        if key in formats:raise ValueError('DUPLICATE_FORMAT')
        formats[key]=dict(zip(('format_id','flags','bytes_packet','frames_packet','bytes_frame','channels','bits','float_interleaved_le'),v))
        formats[key]['rate_hz']=rate
    for side in ('I','O'):
        ids={i for s,i,k in formats if s==side}
        if not 1<=len(ids)<=16 or any((side,i,k) not in formats for i in ids for k in ('V','P')):raise ValueError('INCOMPLETE_FORMATS')
    if {i for s,i,k in formats if s=='I'} & {i for s,i,k in formats if s=='O'}:raise ValueError('SHARED_STREAM_ID')
    return {'pair':pair,'formats':[dict(side=s,stream_id=i,kind=k,**f) for (s,i,k),f in sorted(formats.items())]}

def compatible(snapshot):
    out=snapshot['pair']['O']; streams=[f for f in snapshot['formats'] if f['side']=='O' and f['kind']=='V']
    if len(streams)!=1:return False
    f=streams[0];c=out['channels'];n=out['buffer_frames']
    return (type(c) is int and 1<=c<=64 and type(n) is int and 1<=n<=4096 and
            f['float_interleaved_le']==1 and f['flags']==9 and f['bits']==32 and f['channels']==c and
            f['rate_hz']==out['nominal_rate_hz'] and f['bytes_frame']==4*c and
            f['frames_packet']==1 and f['bytes_packet']==4*c)

def assess(a,b,parent):
    stable=a==b
    pair=parent.assess(a['pair'],b['pair'])
    layout=compatible(b)
    blockers=list(REQUIRED)
    if not stable:blockers.append('DESCRIPTORS_CHANGED')
    if pair['binding']!='READONLY_PAIR_CANDIDATE' or not pair['distinct_endpoint_ids']:blockers.append('PAIR_NOT_READY')
    if not layout:blockers.append('OUTPUT_LAYOUT_NOT_SUPPORTED')
    return {'schema':'freqmed.bench-06.v1','metadata_stable':stable,'pair_binding':pair['binding'],
            'configuration_sha256':parent.fingerprint(b),'output_float32_layout_candidate':layout,
            'snapshot':b,'blockers':blockers,'activation':'HARD_DENIED','physical_backend_available':False,
            'audio_ioproc_registered':False,'stream_opened':False,'physical_output':'NOT_PERFORMED',
            'physical_measurement':'NOT_PERFORMED','authorization':'NONE','certification':'NOT_ISSUED'}

def self_test():
    # Pure structural software vectors, never a hardware observation.
    import copy
    def fmt(**kw):
        f=dict(side='O',kind='V',float_interleaved_le=1,flags=9,bits=32,channels=2,rate_hz=44100,
               bytes_frame=8,frames_packet=1,bytes_packet=8)
        f.update(kw);return f
    base={'pair':{'O':{'channels':2,'buffer_frames':512,'nominal_rate_hz':44100}},'formats':[fmt()]}
    checks=[compatible(base)]
    for field,val in [('flags',41),('bits',24),('channels',1),('rate_hz',48000),('bytes_frame',4),
                      ('frames_packet',2),('bytes_packet',4),('float_interleaved_le',0)]:
        x=copy.deepcopy(base);x['formats'][0][field]=val;checks.append(not compatible(x))
    x=copy.deepcopy(base);x['formats'].append(fmt());checks.append(not compatible(x))
    for val in (0,4097,None):
        x=copy.deepcopy(base);x['pair']['O']['buffer_frames']=val;checks.append(not compatible(x))
    if not all(checks):raise RuntimeError('LAYOUT_TEST_FAILED')
    print('BENCH06_LAYOUT_ASSERTIONS=%d PASS'%len(checks),flush=True)

if __name__=='__main__':self_test()
