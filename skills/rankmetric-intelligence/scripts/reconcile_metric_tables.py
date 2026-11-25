#!/usr/bin/env python3
"""Compare two metric-period-category CSVs; does not fabricate missing zeros."""
import argparse,csv,decimal,json
from pathlib import Path
D=decimal.Decimal
KEY=('metric','period','category')
def read(path):
 result={};issues=[]
 with path.open(encoding='utf-8-sig',newline='') as h:
  rdr=csv.DictReader(h)
  for line,row in enumerate(rdr,2):
   k=tuple((row.get(x) or '').strip() for x in KEY)
   if any(not x for x in k):issues.append({'kind':'incomplete_key','source':str(path),'row':line,'detail':repr(k)});continue
   if k in result:issues.append({'kind':'duplicate_metric_key','source':str(path),'row':line,'detail':repr(k)});continue
   raw=(row.get('value') or '').strip()
   try:n=D(raw)
   except decimal.InvalidOperation:n=None;issues.append({'kind':'invalid_number','source':str(path),'row':line,'detail':repr(raw)})
   result[k]=(n,raw,line)
 return result,issues
def run(left,right,out):
 a,issues=read(left);b,other=read(right);issues+=other
 out.parent.mkdir(parents=True,exist_ok=True);rows=[]
 for k in sorted(set(a)|set(b)):
  la=a.get(k);rb=b.get(k);status='matched';variance=''
  if not la or not rb:status='missing_on_'+('left' if not la else 'right')
  elif la[0] is None or rb[0] is None:status='invalid_numeric_value'
  else:
   variance=str(rb[0]-la[0]);status='matched' if la[0]==rb[0] else 'variance'
  rows.append(dict(zip(KEY,k),left_value=la[1] if la else '',right_value=rb[1] if rb else '',
                   signed_right_minus_left=variance,status=status,left_row=la[2] if la else '',right_row=rb[2] if rb else ''))
 with out.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=[*KEY,'left_value','right_value','signed_right_minus_left','status','left_row','right_row']);w.writeheader();w.writerows(rows)
 with out.with_suffix('.issues.json').open('w',encoding='utf-8') as f:json.dump(issues,f,indent=2)
 return {'compared_metrics':len(rows),'variance_or_missing_or_invalid':sum(r['status']!='matched' for r in rows),'input_issues':len(issues)}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--left',type=Path,required=True);p.add_argument('--right',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();print(json.dumps(run(a.left,a.right,a.output),indent=2))

