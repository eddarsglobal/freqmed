# SPDX-License-Identifier: Apache-2.0
"""Bounded memory archive of validated native records, not a physical acquisition."""
from array import array
MAX_RECORDS=938
PAGE=8
class Archive:
    def __init__(self):self.rows=[]
    def append(self,d):
        if len(self.rows)>=MAX_RECORDS or d["sequence"]!=len(self.rows)+1:
            raise ValueError("ARCHIVE_SEQUENCE_OR_CAP")
        row={k:d[k] for k in ("sequence","processed","expected","rate_hz","count","command_hz","digital_level","duration_ms","state")}
        row["samples"]=array("d",d["samples"])
        self.rows.append(row)
    def page(self,after):
        if type(after) is not int or not 0<=after<=len(self.rows):return None
        rows=[{**r,"samples":r["samples"].tolist()} for r in self.rows[after:after+PAGE]]
        return {"records":rows,"available":len(self.rows),"next":after+len(rows)}
def tests():
    # Structural software-only vectors; never served to the user.
    a=Archive()
    def row(i):
        return dict(sequence=i,processed=i*4096,expected=40960,rate_hz=44100,count=4096,command_hz=828,digital_level=.18,duration_ms=1000,state="RUNNING",samples=[0.0]*4096)
    for i in range(1,11):a.append(row(i))
    p=a.page(0);q=a.page(p["next"])
    checks={"first_page":len(p["records"])==8 and p["next"]==8,"second_page":len(q["records"])==2 and q["next"]==10,
        "ordered":[r["sequence"] for r in p["records"]+q["records"]]==list(range(1,11)),
        "empty_end":a.page(10)["records"]==[],"invalid_cursor":a.page(-1) is None and a.page(11) is None and a.page(True) is None,
        "copy_isolated":True,"sequence_rejected":False,"capacity_bound":MAX_RECORDS==938}
    p["records"][0]["samples"][0]=1
    checks["copy_isolated"]=a.page(0)["records"][0]["samples"][0]==0
    try:a.append(row(12))
    except ValueError:checks["sequence_rejected"]=True
    return checks
