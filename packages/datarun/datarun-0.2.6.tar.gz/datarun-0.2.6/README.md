# datarun

**datarun** is a lightweight Python package that helps you cleanse your pandas DataFrames with minimal configuration.  
It supports automatic handling of duplicates, missing values, constant columns, and type conversion.

## Features

- Drop duplicate rows
- Handle missing values using mean, median, mode, or drop
- Drop constant-value columns
- Convert string-based numeric columns to proper types
- Configurable and simple to use

## Example: Linear Regression

```python
from datarun import LinearRegressionCustom
import pandas as pd

data = pd.read_csv("Salary_dataset.csv")
X = data[['YearsExperience']]
y = data['Salary']

model = LinearRegressionCustom(method='gradient_descent', learning_rate=0.01, epochs=5000)
model.fit(X, y)
preds = model.predict(X)
print(model.get_params())

## Installation

pip install datarun
