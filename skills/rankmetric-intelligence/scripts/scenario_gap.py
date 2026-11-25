#!/usr/bin/env python3
"""User-defined target gap; not an official ranking-score forecast."""
import argparse,json
from decimal import Decimal,InvalidOperation

def calc(current,target):
 c,t=Decimal(str(current)),Decimal(str(target))
 if not c.is_finite() or not t.is_finite():raise ValueError('Inputs must be finite numbers')
 delta=t-c
 return {'current':str(c),'target':str(t),'signed_change':str(delta),'nonnegative_target_gap':str(max(Decimal(0),delta)),
         'relative_change_percent':str(delta/abs(c)*100) if c!=0 else None,
         'status':'user_defined_scenario_not_official_score'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--current',required=True);p.add_argument('--target',required=True);p.add_argument('--unit',default='units')
 a=p.parse_args();result=calc(a.current,a.target);result['unit']=a.unit;print(json.dumps(result,indent=2))

