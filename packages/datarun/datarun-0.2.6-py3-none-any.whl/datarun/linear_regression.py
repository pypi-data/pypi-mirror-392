import numpy as np

class LinearRegression:
    def __init__(self, method='gradient_descent', learning_rate=0.01, epochs=1000, scale_features=True):
        self.method = method
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.scale_features = scale_features
        self.w = None
        self.b = None
        self.mean_X = None
        self.std_X = None

    def fit(self, X, y):
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)

        m, n = X.shape

        if self.scale_features and self.method == 'gradient_descent':
            self.mean_X = X.mean(axis=0)
            self.std_X = X.std(axis=0)
            X = (X - self.mean_X) / self.std_X

        if self.method == 'normal_equation':
            X_b = np.hstack([X, np.ones((m,1))])
            theta = np.linalg.pinv(X_b.T @ X_b) @ (X_b.T @ y)
            self.w = theta[:-1]
            self.b = theta[-1]

        elif self.method == 'gradient_descent':
            self.w = np.zeros(n)
            self.b = 0
            for _ in range(self.epochs):
                y_pred = np.dot(X, self.w) + self.b
                error = y_pred - y
                dw = (1/m) * np.dot(X.T, error)
                db = (1/m) * np.sum(error)
                self.w -= self.learning_rate * dw
                self.b -= self.learning_rate * db
        else:
            raise ValueError("Method must be 'gradient_descent' or 'normal_equation'")

    def predict(self, X):
        X = np.array(X, dtype=float)
        if self.scale_features and self.mean_X is not None:
            X = (X - self.mean_X) / self.std_X
        return np.dot(X, self.w) + self.b

    def get_params(self):
        return self.w, self.b