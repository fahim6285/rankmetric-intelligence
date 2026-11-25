import unittest,sys,tempfile,csv
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'scripts'))
from consolidate_sdg_csv import run,normdoi
from reconcile_metric_tables import run as reconcile
from scenario_gap import calc
class ScriptsTest(unittest.TestCase):
 def test_normalize_doi(self):self.assertEqual(normdoi('https://doi.org/10.5555/ABC.001'), '10.5555/abc.001')
 def test_sdg_consolidation(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'run'
   x=run([BASE/'examples/sdg_3.csv', BASE/'examples/sdg_9.csv'],out)
   self.assertEqual(x['input_source_rows'],6)
   self.assertEqual(x['unique_work_groups'],4)
   self.assertEqual(x['duplicate_groups'],2)
   with (out/'year_summary.csv').open() as f:rows=list(csv.DictReader(f))
   self.assertEqual([int(r['unique_works']) for r in rows],[2,2])
   self.assertEqual([int(r['sdg_incidences']) for r in rows],[4,2])
 def test_multiple_unkeyed_title_duplicates(self):
  with tempfile.TemporaryDirectory() as tmp:
   paths=[]
   for idx in (3,9,11):
    p=Path(tmp)/f'sdg_{idx}.csv'
    p.write_text('Title,Publication Year\n"Some sufficiently unique synthetic title",2024\n')
    paths.append(p)
   result=run(paths,Path(tmp)/'out')
   self.assertEqual(result['unique_work_groups'],1)
   self.assertEqual(result['duplicate_groups'],1)
 def test_reconciliation(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'compare.csv'
   x=reconcile(BASE/'examples/metric_reference_a.csv',BASE/'examples/metric_reference_b.csv',out)
   self.assertEqual(x['variance_or_missing_or_invalid'],1)
 def test_scenario(self):
  x=calc('10','12.5')
  self.assertEqual(x['nonnegative_target_gap'],'2.5')
  self.assertEqual(x['relative_change_percent'],'25.00')
  self.assertIsNone(calc('0','1')['relative_change_percent'])
if __name__=='__main__':unittest.main()

