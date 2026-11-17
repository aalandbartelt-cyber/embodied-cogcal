import unittest
from verify_smoke import check_initial_pair, check_injection, clipped_joints, check_contract_pair

class TestSmokeChecks(unittest.TestCase):
    def test_injection_is_only_q5_and_correct_dose(self):
        record={'policy_target_rad':[0.,0.,0.,0.,0.,0.], 'raw_target_rad':[0.,0.,0.,0.,-0.125,0.]}
        check_injection(record, -0.125)
        record['raw_target_rad'][1]=0.1
        with self.assertRaises(ValueError): check_injection(record, -0.125)

    def test_initial_pair_requires_same_image_and_joint_state(self):
        row={'seed':14100, 'delta_mm':1.1, 'source_xyz_m':[1,2,3], 'goal_xyz_m':[3,2,1], 'yaw_deg':-15}
        trace={'q_before_rad':[0]*6,'rgb_sha256':'abc'}
        check_initial_pair(row, trace, dict(row), dict(trace))
        different={**trace, 'rgb_sha256':'def'}
        with self.assertRaises(ValueError): check_initial_pair(row, trace, row, different)

    def test_clipping_counts_changed_joints(self):
        record={'raw_target_rad':[0.0]*6,'command_rad':[0.0,0.0,0.0,0.0,0.2,0.0]}
        self.assertEqual(clipped_joints(record), [4])

    def test_contract_pair_rejects_different_checkpoint(self):
        keys=('checkpoint_sha256','carrier_pyc_sha256','training_contract_sha256','source_sha256','seeds','control_budget','control_fps','horizon','execute')
        base={key: 'same' for key in keys}
        changed={**base,'checkpoint_sha256':'different'}
        with self.assertRaises(ValueError): check_contract_pair(base, changed)

if __name__ == '__main__': unittest.main()
