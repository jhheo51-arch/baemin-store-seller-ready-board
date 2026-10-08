import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
from policy_model import POLICIES, simulate_policy


class PolicyModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = pd.read_csv(ROOT / 'data/work_tasks.csv')

    def test_all_published_policy_metrics_recomputed(self):
        expected = json.loads((ROOT / 'analysis/summary.json').read_text(encoding='utf-8'))['policy_metrics']
        actual = [simulate_policy(self.tasks, policy) for policy in POLICIES]
        self.assertEqual(actual, expected)
        for result in actual:
            self.assertEqual(result['completed_tasks'] + result['unresolved_tasks'], len(self.tasks))

    def test_small_fifo_example_and_input_preservation(self):
        tasks = pd.DataFrame([
            dict(task_id='a',release_day=0,effort_hours=2,repeat_contact_count=0,severity=1,progress_stage=4),
            dict(task_id='b',release_day=0,effort_hours=2,repeat_contact_count=0,severity=1,progress_stage=4),
        ])
        before = tasks.copy(deep=True)
        result = simulate_policy(tasks, POLICIES[0], days=2, capacity_per_day=2)
        self.assertEqual(result['completed_tasks'], 2)
        self.assertEqual(result['median_wait_days'], 0.5)
        self.assertEqual(result['unresolved_tasks'], 0)
        pd.testing.assert_frame_equal(tasks, before)

    def test_empty_and_zero_capacity_do_not_invent_rates(self):
        result = simulate_policy(self.tasks.iloc[:0], POLICIES[0])
        self.assertIsNone(result['completion_rate'])
        result = simulate_policy(self.tasks, POLICIES[0], capacity_per_day=0)
        self.assertEqual(result['completed_tasks'], 0)
        self.assertEqual(result['unresolved_tasks'], len(self.tasks))
        self.assertIsNone(result['sla_3day_rate'])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            simulate_policy(self.tasks, 'unknown')
        for column, value in [('release_day',56),('release_day',0.5),('effort_hours',0),('effort_hours',float('nan'))]:
            changed=self.tasks.copy();changed[column]=changed[column].astype(float);changed.loc[0,column]=value
            with self.subTest(column=column,value=value), self.assertRaises(ValueError):
                simulate_policy(changed, POLICIES[0])
        with self.assertRaises(ValueError):
            simulate_policy(pd.concat([self.tasks,self.tasks.iloc[:1]]), POLICIES[0])

    def test_generator_recreates_the_four_published_csv_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'generated'
            subprocess.run([sys.executable,str(ROOT/'analysis/generate_data.py'),'--output-dir',str(output)],check=True)
            for name in ['sellers','stage_history','inquiries','work_tasks']:
                expected=pd.read_csv(ROOT/'data'/f'{name}.csv')
                actual=pd.read_csv(output/f'{name}.csv')
                pd.testing.assert_frame_equal(actual,expected)
            # The generator must not replace already-created inputs.
            attempt=subprocess.run([sys.executable,str(ROOT/'analysis/generate_data.py'),'--output-dir',str(output)],capture_output=True)
            self.assertNotEqual(attempt.returncode,0)


if __name__ == '__main__':
    unittest.main()
