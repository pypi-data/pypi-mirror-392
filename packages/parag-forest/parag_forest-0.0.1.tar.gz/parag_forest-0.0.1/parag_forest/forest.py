import numpy as np

# ------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------

def mse(y):
    """Mean squared error for a node."""
    return np.mean((y - np.mean(y)) ** 2)

def bootstrap_sample(X, y):
    """Create a bootstrap sample (sampling with replacement)."""
    n_samples = X.shape[0]
    indices = np.random.randint(0, n_samples, n_samples)
    return X[indices], y[indices]

# ------------------------------------------------------------
# Decision Tree Regressor (Simple)
# ------------------------------------------------------------

class DecisionTreeRegressor:
    def __init__(self, max_depth=5, min_samples_split=2, n_features=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_features = n_features
        self.tree = None

    def fit(self, X, y):
        self.n_features = X.shape[1] if not self.n_features else self.n_features
        self.tree = self._build_tree(X, y, depth=0)

    def _best_split(self, X, y):
        m, n = X.shape
        best_feature, best_threshold = None, None
        best_mse = float("inf")
        features = np.random.choice(n, self.n_features, replace=False)

        for feature in features:
            thresholds = np.unique(X[:, feature])
            for threshold in thresholds:
                left_mask = X[:, feature] <= threshold
                right_mask = X[:, feature] > threshold

                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    continue

                left_mse = mse(y[left_mask])
                right_mse = mse(y[right_mask])
                weighted_mse = (left_mask.sum()*left_mse + right_mask.sum()*right_mse) / m

                if weighted_mse < best_mse:
                    best_mse = weighted_mse
                    best_feature = feature
                    best_threshold = threshold

        return best_feature, best_threshold

    def _build_tree(self, X, y, depth):
        num_samples, num_features = X.shape

        if depth >= self.max_depth or num_samples < self.min_samples_split:
            return np.mean(y)

        feature, threshold = self._best_split(X, y)

        if feature is None:
            return np.mean(y)

        left_mask = X[:, feature] <= threshold
        right_mask = X[:, feature] > threshold

        left_child = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._build_tree(X[right_mask], y[right_mask], depth + 1)

        return (feature, threshold, left_child, right_child)

    def _predict_sample(self, x, node):
        if not isinstance(node, tuple):
            return node

        feature, threshold, left_child, right_child = node

        if x[feature] <= threshold:
            return self._predict_sample(x, left_child)
        else:
            return self._predict_sample(x, right_child)

    def predict(self, X):
        return np.array([self._predict_sample(sample, self.tree) for sample in X])

# ------------------------------------------------------------
# Random Forest Regressor
# ------------------------------------------------------------

class RandomForestRegressor:
    def __init__(self, n_estimators=100, max_depth=5,
                 min_samples_split=2, max_features="sqrt"):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []

    def _get_n_features(self, n_total):
        if self.max_features == "sqrt":
            return int(np.sqrt(n_total))
        elif self.max_features == "log2":
            return int(np.log2(n_total))
        else:
            return n_total

    def fit(self, X, y):
        self.trees = []
        n_features = self._get_n_features(X.shape[1])

        for _ in range(self.n_estimators):
            X_sample, y_sample = bootstrap_sample(X, y)
            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                n_features=n_features
            )
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)

    def predict(self, X):
        tree_preds = np.array([tree.predict(X) for tree in self.trees])
        return np.mean(tree_preds, axis=0)
