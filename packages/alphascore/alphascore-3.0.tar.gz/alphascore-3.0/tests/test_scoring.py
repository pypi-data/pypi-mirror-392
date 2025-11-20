import pandas as pd
from alphascore import DataQualityScore

def test_compute_basic():
    df = pd.DataFrame({'a':[1,2,3,None], 'b':['x','y','y','']})
    engine = DataQualityScore(df, name='t')
    res = engine.compute()
    assert 'final_score' in res
    assert isinstance(res['final_score'], float)
