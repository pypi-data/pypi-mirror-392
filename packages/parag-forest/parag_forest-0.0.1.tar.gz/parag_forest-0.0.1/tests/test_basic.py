import numpy as np
from parag_forest import RandomForestRegressor

def test_fit_predict():
    X = np.random.rand(20, 3)
    y = np.random.rand(20)

    model = RandomForestRegressor(n_estimators=5, max_depth=3)
    model.fit(X, y)
    preds = model.predict(X)

    assert preds.shape[0] == X.shape[0]
    assert np.all(np.isfinite(preds))
