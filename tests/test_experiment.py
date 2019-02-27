
import unittest
import os
from pytest import approx
import pandas as pd
import numpy as np
import emat
from emat.scope.scope import Scope
from emat.database.sqlite.sqlite_db import SQLiteDB




class TestExperimentMethods(unittest.TestCase):
    ''' 
        tests generating experiments      
    '''
    #  
    # one time test setup
    #
    scope_file = emat.package_file("scope","tests","scope_test.yaml")
    scp = Scope(scope_file)

    db_test = SQLiteDB(":memory:", initialize=True)
    scp.store_scope(db_test)

    def test_latin_hypercube(self):
        exp_def = self.scp.design_experiments(
            n_samples_per_factor=10,
            random_seed=1234,
            sampler='lhs',
            db=self.db_test,
        )
        assert len(exp_def) == self.scp.n_sample_factors()*10
        assert (exp_def['TestRiskVar'] == 1.0).all()
        assert (exp_def['Land Use - CBD Focus']).mean() == approx(1.0326, abs=1e-3)
        assert (exp_def['Freeway Capacity']).mean() == approx(1.5, abs=1e-3)

        exp_def2 = self.db_test.read_experiment_parameters(self.scp.name,'lhs')
        assert (exp_def[exp_def2.columns] == exp_def2).all().all()

    def test_monte_carlo(self):
        exp_def = self.scp.design_experiments(
            n_samples_per_factor=10,
            random_seed=1234,
            sampler='mc',
            db=self.db_test,
        )
        assert len(exp_def) == self.scp.n_sample_factors()*10
        assert (exp_def['TestRiskVar'] == 1.0).all()
        assert (exp_def['Land Use - CBD Focus']).mean() == approx(1.04, abs=0.01)
        assert (exp_def['Freeway Capacity']).mean() == approx(1.5, abs=0.01)

        exp_def2 = self.db_test.read_experiment_parameters(self.scp.name,'mc')
        assert (exp_def[exp_def2.columns] == exp_def2).all().all()

    def test_sensitivity_tests(self):
        exp_def = self.scp.design_experiments(
            sampler='uni',
            db=self.db_test,
        )
        cols = ['TestRiskVar', 'Land Use - CBD Focus', 'Freeway Capacity',
           'Auto IVTT Sensitivity', 'Shared Mobility',
           'Kensington Decommissioning', 'LRT Extension']
        correct = '{"TestRiskVar":{"0":1.0,"1":1.0,"2":1.0,"3":1.0,"4":1.0,"5":1.0,"6":1.0,"7":1.0},' \
                  '"Land Use - CBD Focus":{"0":1.0,"1":0.82,"2":1.37,"3":1.0,"4":1.0,"5":1.0,"6":1.0,"7":1.0},' \
                  '"Freeway Capacity":{"0":1.0,"1":1.0,"2":1.0,"3":2.0,"4":1.0,"5":1.0,"6":1.0,"7":1.0},' \
                  '"Auto IVTT Sensitivity":{"0":1.0,"1":1.0,"2":1.0,"3":1.0,"4":0.75,"5":1.0,"6":1.0,"7":1.0},' \
                  '"Shared Mobility":{"0":0.0,"1":0.0,"2":0.0,"3":0.0,"4":0.0,"5":1.0,"6":0.0,"7":0.0},' \
                  '"Kensington Decommissioning":{"0":false,"1":false,"2":false,"3":false,"4":false,' \
                  '"5":false,"6":true,"7":false},"LRT Extension":{"0":false,"1":false,"2":false,"3":false,' \
                  '"4":false,"5":false,"6":false,"7":true}}'
        correct = pd.read_json(correct)
        for k in cols:
            assert (exp_def[k].values == approx(correct[k].values))

        exp_def2 = self.db_test.read_experiment_parameters(self.scp.name,'uni')
        for k in cols:
            assert (exp_def2[k].values == approx(correct[k].values))


if __name__ == '__main__':
    unittest.main()