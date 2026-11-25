#!/usr/bin/env python3
"""Conservative multi-SDG publication consolidation from CSV files; standard library only.

Usage: python consolidate_sdg_csv.py --inputs examples/sdg_3.csv examples/sdg_9.csv --output /tmp/rankmetric_demo
"""
import argparse,csv,re,json
from collections import defaultdict,Counter
from pathlib import Path

ALIASES={
 'title':['title','document title','article title','publication title'],
 'year':['publication year','year','pub year','publication_year'],
 'doi':['doi','digital object identifier'],
 'eid':['eid','scopus eid','scopus id','database id'],
 'sdg':['sdg','sdg number','sustainable development goal','sdg_id'],
 'document_type':['document type','type','publication type'],
}
def normkey(s):return re.sub(r'[^a-z0-9]+',' ',str(s).lower()).strip()
def normtitle(s):return normkey(s)
def normdoi(s):
 s=str(s or '').strip().lower();s=re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi\s*:\s*)','',s)
 return s.strip(' .;,')
def normeid(s):return str(s or '').strip().lower()
def choose_field(row,field):
 wanted={normkey(a) for a in ALIASES[field]};return next((v for k,v in row.items() if normkey(k) in wanted and v is not None),'')
def sdg_from_name(path):
 m=re.search(r'(?<!\d)sdg[\s_-]*0?([1-9]|1[0-7])(?!\d)',path.stem,re.I)
 return int(m.group(1)) if m else None
def write_csv(path,rows,fields):
 with path.open('w',encoding='utf-8',newline='') as fh:
  writer=csv.DictWriter(fh,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
def run(paths,out):
 out.mkdir(parents=True,exist_ok=True)
 rows=[];issues=[];source_manifest=[]
 for path in paths:
  path=Path(path);sdg_file=sdg_from_name(path);n=0
  with path.open('r',encoding='utf-8-sig',newline='') as f:
   reader=csv.DictReader(f)
   if not reader.fieldnames:issues.append({'kind':'empty_file','source':path.name,'detail':'No headers'});continue
   available={normkey(x) for x in reader.fieldnames}
   missing=[f for f in ['title','year'] if not any(normkey(a) in available for a in ALIASES[f])]
   if missing:
    issues.append({'kind':'missing_required_columns','source':path.name,'detail':','.join(missing)})
    continue
   for line,row in enumerate(reader,2):
    n+=1;title=choose_field(row,'title').strip();yr_raw=choose_field(row,'year').strip()
    doi=normdoi(choose_field(row,'doi'));eid=normeid(choose_field(row,'eid'))
    sdg_raw=choose_field(row,'sdg').strip();sdgs=[]
    if sdg_raw:
     for x in re.split(r'[,;|/]',sdg_raw):
      m=re.search(r'\b(?:SDG\s*)?(1[0-7]|[1-9])\b',x,re.I)
      if m:sdgs.append(int(m.group(1)))
      elif x.strip():issues.append({'kind':'invalid_sdg','source':f'{path.name}:{line}','detail':x.strip()})
    elif sdg_file:sdgs=[sdg_file]
    else:issues.append({'kind':'missing_sdg','source':f'{path.name}:{line}','detail':'No SDG column or identifying filename'})
    year=int(yr_raw) if re.fullmatch(r'(18|19|20|21)\d{2}',yr_raw) else None
    if not year:issues.append({'kind':'invalid_year','source':f'{path.name}:{line}','detail':yr_raw})
    if not title:issues.append({'kind':'missing_title','source':f'{path.name}:{line}','detail':'Empty title'})
    # Generic identifiers are retained, but not treated as verified bibliographic claims.
    if doi and not re.fullmatch(r'10\.\d{4,9}/\S+',doi):issues.append({'kind':'suspicious_doi','source':f'{path.name}:{line}','detail':doi})
    rows.append({'source_file':path.name,'source_row':line,'title':title,'title_key':normtitle(title),
                'year':year,'doi':doi,'eid':eid,'doc_type':choose_field(row,'document_type').strip(),
                'sdgs':sorted(set(sdgs)),'raw_json':json.dumps(row,ensure_ascii=False)})
  source_manifest.append({'source_file':path.name,'input_rows':n,'sdg_from_filename':sdg_file or ''})
 # Identity resolution: DOI and EID first. Only connect unkeyed rows by an unambiguous title-year.
 doi_to_key={};eid_to_key={};groups={};title_to_keys=defaultdict(set)
 def add_new(r,i):
  key=f'WORK{i:06d}';groups[key]=[];return key
 for i,r in enumerate(rows,1):
  if not r['title'] or r['year'] is None:
   issues.append({'kind':'unusable_identity','source':f"{r['source_file']}:{r['source_row']}",'detail':'Title and valid year required'})
   continue
  key=None
  if r['doi'] and r['doi'] in doi_to_key:key=doi_to_key[r['doi']]
  if not key and r['eid'] and r['eid'] in eid_to_key:key=eid_to_key[r['eid']]
  if not key:key=add_new(r,i)
  groups[key].append(r)
  if r['doi'] and r['doi'] in doi_to_key and doi_to_key[r['doi']]!=key:
   issues.append({'kind':'identifier_conflict','source':r['source_file'],'detail':r['doi']})
  if r['doi']:doi_to_key.setdefault(r['doi'],key)
  if r['eid']:eid_to_key.setdefault(r['eid'],key)
  title_to_keys[(r['title_key'],r['year'])].add(key)
 # Combine title/year-only records first, regardless of their number.
 unkeyed=defaultdict(list)
 for key,grp in list(groups.items()):
  if len(grp)==1 and not grp[0]['doi'] and not grp[0]['eid']:
   unkeyed[(grp[0]['title_key'],grp[0]['year'])].append(key)
 for label,keys in unkeyed.items():
  anchor=sorted(keys)[0]
  for key in sorted(keys)[1:]:
   groups[anchor].extend(groups.pop(key))
 # Reconcile unkeyed titles to a unique positively identified match only.
 for key in list(groups):
  if key not in groups:continue
  grp=groups[key]
  if any(r['doi'] or r['eid'] for r in grp):continue
  title_year=(grp[0]['title_key'],grp[0]['year'])
  candidates=[k for k,g in groups.items() if k!=key and any(r['doi'] or r['eid'] for r in g)
              and any((r['title_key'],r['year'])==title_year for r in g)]
  if len(candidates)==1:
   groups[candidates[0]].extend(grp);del groups[key]
  elif len(candidates)>1:
   refs='; '.join(f"{r['source_file']}:{r['source_row']}" for r in grp)
   issues.append({'kind':'ambiguous_title_year','source':refs,'detail':f'{len(candidates)} positively identified candidate works'})
 # Detect remaining title+year conflict across separately keyed works.
 remaining=defaultdict(list)
 for key,g in groups.items():remaining[(g[0]['title_key'],g[0]['year'])].append(key)
 for (title,yr),keys in remaining.items():
  if len(keys)>1:issues.append({'kind':'same_title_year_multiple_identities','source':str(yr),'detail':f'{title}: {len(keys)} works; manual review'})
 unique=[];duplicate=[];sdg_memberships=[];year_totals=defaultdict(lambda:{'unique_works':0,'sdg_incidences':0,'source_rows':0})
 for idx,(key,group) in enumerate(sorted(groups.items()),1):
  uid=f'RW{idx:06d}';years={r['year'] for r in group};dois={r['doi'] for r in group if r['doi']};eids={r['eid'] for r in group if r['eid']}
  titles={r['title_key'] for r in group};sdgs=sorted({s for r in group for s in r['sdgs']})
  conflicts=[]
  if len(years)>1:conflicts.append('year')
  if len(dois)>1:conflicts.append('doi')
  if len(eids)>1:conflicts.append('eid')
  if len(titles)>1:conflicts.append('title')
  year=group[0]['year'] if not conflicts else None
  if conflicts:issues.append({'kind':'intra_work_conflict','source':uid,'detail':','.join(conflicts)})
  source_refs='; '.join(f"{r['source_file']}:{r['source_row']}" for r in group)
  unique.append({'work_id':uid,'title':group[0]['title'],'publication_year':year or '', 'doi':sorted(dois)[0] if len(dois)==1 else '',
   'eid':sorted(eids)[0] if len(eids)==1 else '', 'sdgs':';'.join(str(n) for n in sdgs), 'source_row_count':len(group),'source_rows':source_refs,
   'review_status':'review_required' if conflicts else 'provisional_deduplicated'})
  if len(group)>1:duplicate.append({'work_id':uid,'source_row_count':len(group),'source_rows':source_refs,'matching_basis':'identifier/title-year; verify conflicting metadata'})
  if year is not None:
   year_totals[year]['unique_works']+=1;year_totals[year]['source_rows']+=len(group);year_totals[year]['sdg_incidences']+=len(sdgs)
   for sdg in sdgs:sdg_memberships.append({'work_id':uid,'publication_year':year,'sdg':sdg,'source_rows':source_refs})
 raw=[{'source_file':r['source_file'],'source_row':r['source_row'],'title':r['title'],'publication_year':r['year'] or '', 'doi':r['doi'],'eid':r['eid'],'sdgs':';'.join(map(str,r['sdgs'])),'raw_json':r['raw_json']} for r in rows]
 write_csv(out/'raw_source_rows.csv',raw,['source_file','source_row','title','publication_year','doi','eid','sdgs','raw_json'])
 write_csv(out/'unique_publications.csv',unique,['work_id','title','publication_year','doi','eid','sdgs','source_row_count','source_rows','review_status'])
 write_csv(out/'duplicate_groups.csv',duplicate,['work_id','source_row_count','source_rows','matching_basis'])
 write_csv(out/'issues_to_review.csv',issues,['kind','source','detail'])
 write_csv(out/'source_manifest.csv',source_manifest,['source_file','input_rows','sdg_from_filename'])
 write_csv(out/'sdg_memberships.csv',sdg_memberships,['work_id','publication_year','sdg','source_rows'])
 summary=[{'publication_year':yr,**vals} for yr,vals in sorted(year_totals.items())]
 write_csv(out/'year_summary.csv',summary,['publication_year','unique_works','source_rows','sdg_incidences'])
 sdg_counts=Counter((int(r['publication_year']),int(r['sdg'])) for r in sdg_memberships)
 sdg_summary=[{'publication_year':yr,'sdg':s,'unique_work_memberships':sdg_counts[(yr,s)]} for yr in sorted(year_totals) for s in range(1,18)]
 write_csv(out/'sdg_year_summary.csv',sdg_summary,['publication_year','sdg','unique_work_memberships'])
 stats={'input_source_rows':len(rows),'unique_work_groups':len(unique),'duplicate_groups':len(duplicate),'review_issues':len(issues),'by_year':summary}
 (out/'run_summary.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
 return stats
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',nargs='+',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
 a=p.parse_args();print(json.dumps(run(a.inputs,a.output),indent=2))

