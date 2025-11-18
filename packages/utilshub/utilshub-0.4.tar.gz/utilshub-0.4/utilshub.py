import inspect

code_1a = """
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore, skew

df = pd.read_csv("iris.csv")
print(df.head())
print(df.tail())
print(df.shape)

categorical_cols = df.select_dtypes(include='object').columns
numerical_cols = df.select_dtypes(include=np.number).columns
print("Num COL:", len(categorical_cols))
print("Cat COL:", len(numerical_cols))

print(df[numerical_cols].describe())
df[numerical_cols].mode()
print(df.isnull().sum())

plt.boxplot(df[numerical_cols].corr(), showfliers=False)
plt.show()

z_score = zscore(df[numerical_cols])
outliers = (abs(z_score) > 3)
print(df[outliers.any(axis=1)])

corr_matrix = df[numerical_cols].corr()
print("High corr : ", corr_matrix > 0.7)
print("Negative corr : ", corr_matrix < 0.7)
print("No corr : ", corr_matrix[(corr_matrix < -0.1) & (corr_matrix > 0.1)])

skew = df[numerical_cols]
print("Right Skew:", skew > 0.5)
print("Left Skew:", skew < 0.5)
print("No Skew:", skew)

df[categorical_cols].value_counts().plot(kind='bar')
plt.xlabel('Category')
plt.ylabel('Count')
plt.title(f'Bar Plot')
plt.show()

sns.swarmplot(x=df['SepalLengthCm'])
plt.title('Swarm Plot of SepalLengthCm')
plt.xlabel('SepalLengthCm')
plt.show()

sns.violinplot(x=df['SepalLengthCm'])
plt.title('Violin Plot of SepalLengthCm')
plt.xlabel('SepalLengthCm')
plt.show()

plt.scatter(df['SepalLengthCm'], df['SepalWidthCm'])
plt.xlabel('SepalLengthCm')
plt.ylabel('SepalWidthCm')
plt.title('Scatter Plot: SepalLengthCm vs SepalWidthCm')
plt.show()

cat_col = 'Species'
num_col = 'SepalLengthCm'
sns.boxplot(x=df[cat_col], y=df[num_col])
plt.title(f'Boxplot of {num_col} across {cat_col}')
plt.xlabel(cat_col)
plt.ylabel(num_col)
plt.xticks(rotation=45)
plt.show()

sns.countplot(x=df[cat_col])
plt.xlabel("species")
plt.ylabel("count")
plt.show()

sns.pairplot(df, hue='Species')
plt.show()
"""

code_1b = """
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from scipy.stats import zscore

df = pd.read_csv("Stores1b.csv")
missing_percent = df.isnull().mean() * 100
print("Missing values %:", missing_percent)

# Mean imputation for numerical columns
for col in df.select_dtypes(include=[np.number]).columns:
    if missing_percent[col] < 10:
        df[col].fillna(df[col].mean(), inplace=True)

# Mode imputation for categorical columns
for col in df.select_dtypes(include='object').columns:
    if missing_percent[col] < 10:
        df[col].fillna(df[col].mode()[0], inplace=True)

# Drop columns with >10% missing
cols_to_drop = missing_percent[missing_percent > 10].index
df.drop(columns=cols_to_drop, inplace=True)

# Outlier treatment
z_scores = zscore(df['Quantity'])
df = df[(np.abs(z_scores) <= 3)]

# Remove duplicates
df.drop_duplicates(inplace=True)

# Normalization
scaler = MinMaxScaler()
df['Age_MinMax'] = scaler.fit_transform(df[['Age']])

scaler_z = StandardScaler()
df['Age_Zscore'] = scaler_z.fit_transform(df[['Age']])

# Encoding
le = LabelEncoder()
df['Payment_LabelEncoded'] = le.fit_transform(df['Payment'])
df = pd.get_dummies(df, columns=['Payment'])

print("Preprocessing Complete")
print(df.head())
"""

code_2 = """
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split

df = pd.read_csv('Stores1b.csv')
X = df.drop('Price', axis=1)
y = df['Price']
X = X.select_dtypes(include=['number'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Variance Threshold
selector = VarianceThreshold(threshold=0.01)
X_train_sel = selector.fit_transform(X_train_scaled)
X_test_sel = selector.transform(X_test_scaled)
print("Selected features after variance threshold")

# PCA
pca = PCA(n_components=5)
X_train_pca = pca.fit_transform(X_train_sel)
X_test_pca = pca.transform(X_test_sel)
print("Explained Variance Ratio:", pca.explained_variance_ratio_)
"""

code_3 = """
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

df = pd.read_csv("Algerian_forest_fires_dataset.csv", skiprows=1)
df = df[['Temperature', 'FWI']].apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

X = df['Temperature'].values
Y = df['FWI'].values

# Calculate slope and intercept
x_mean = np.mean(X)
y_mean = np.mean(Y)
b1 = np.sum((X - x_mean) * (Y - y_mean)) / np.sum((X - x_mean) ** 2)
b0 = y_mean - b1 * x_mean

# Predict
Y_pred = b0 + b1 * X

# Metrics
sse = np.sum((Y - Y_pred) ** 2)
rmse = np.sqrt(mean_squared_error(Y, Y_pred))
r2 = r2_score(Y, Y_pred)

print(f"Slope (b1): {b1:.4f}")
print(f"Intercept (b0): {b0:.4f}")
print(f"SSE: {sse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R² Score: {r2:.4f}")

plt.scatter(X, Y, color='green', label='Actual Data')
plt.plot(X, Y_pred, color='red', label='Regression Line')
plt.xlabel('Temperature')
plt.ylabel('FWI')
plt.title('Linear Regression')
plt.legend()
plt.show()
"""

code_4 = """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

df = pd.read_csv("BankNote_Authentication.csv")

# Preprocessing
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].fillna(df[col].mode()[0])
    else:
        df[col] = df[col].fillna(df[col].mean())

X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values
y = np.where(y > 0, 1, 0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Single Layer Perceptron
np.random.seed(42)
weights = np.random.rand(X.shape[1])
bias = np.random.rand()
learning_rate = 0.01
epochs = 100

# Training loop
for epoch in range(epochs):
    for i in range(len(X_train)):
        x = X_train[i]
        y_true = y_train[i]
        y_pred = 1 if np.dot(x, weights) + bias > 0 else 0
        error = y_true - y_pred
        weights += learning_rate * error * x
        bias += learning_rate * error

print("Single Layer Perceptron Training Complete")
print("Final Weights:", weights)
print("Final Bias:", bias)
"""

code_5 = """
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

df = pd.read_csv("HR Data.csv")

# Handle missing values
for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col].fillna(df[col].median(), inplace=True)
    else:
        df[col].fillna(df[col].mode()[0], inplace=True)

# Encoding categorical variables
for col in df.columns:
    if not pd.api.types.is_numeric_dtype(df[col]):
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

# Split features and target
TARGET_COL = "salary"
X = df.drop(columns=[TARGET_COL])
y = df[TARGET_COL]

# Normalize
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42)

# MLP Model
class MLP(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )
    
    def forward(self, x):
        return self.layers(x)

model = MLP(X.shape[1], 1)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

print("MLP Model with Backpropagation Defined")
print("Training starts...")

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1)

for epoch in range(100):
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

print("Training Complete")
"""

code_6 = """
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

df = pd.read_csv("Solar.csv")

# Remove unnamed column
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# Remove target
target = df["Solar Radiation"]
df = df.drop(columns=["Solar Radiation"])

# Fill missing values
df = df.fillna(df.mean())

# Scale
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df)

# Hierarchical Clustering
cluster = AgglomerativeClustering(n_clusters=3, linkage="single", metric="euclidean")
labels = cluster.fit_predict(df_scaled)

print("Hierarchical Clustering Complete")
print("Number of unique clusters:", len(np.unique(labels)))
print("Cluster labels:", labels[:10])

# Dendrogram
Z = linkage(df_scaled, method='single')
dendrogram(Z)
plt.title('Hierarchical Clustering Dendrogram')
plt.show()
"""

code_7 = """
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

df = pd.read_csv("Heart.csv")

# Label encoding for categorical columns
label_enc = LabelEncoder()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = label_enc.fit_transform(df[col].astype(str))

# Remove target if present
if 'target' in df.columns:
    X = df.drop(columns=['target'])
else:
    X = df.copy()

# Normalization
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

print("Fuzzy C-Means Clustering Implementation")
print("Data shape:", X_scaled.shape)

# Fuzzy C-Means Parameters
c = 3  # number of clusters
m = 2  # fuzziness parameter
epsilon = 1e-5
max_iterations = 100

# Initialize membership matrix
U = np.random.dirichlet(np.ones(c), len(X_scaled))

print("Fuzzy C-Means Algorithm Running...")
for iteration in range(max_iterations):
    # Calculate cluster centers
    Um = U ** m
    C = (Um.T @ X_scaled) / (Um.T.sum(axis=1, keepdims=True) + 1e-10)
    
    # Update membership matrix
    D = np.linalg.norm(X_scaled[:, np.newaxis] - C, axis=2)
    U = (1 / D) ** (1 / (m - 1))
    U = U / U.sum(axis=1, keepdims=True)

print("Fuzzy C-Means Clustering Complete")
print("Final Cluster Centers shape:", C.shape)
"""

code_8 = """
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

df = pd.read_csv("HR Data.csv")

# Handle missing values
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].fillna(df[col].mode()[0])
    else:
        df[col] = df[col].fillna(df[col].mean())

# Remove target columns
target_cols = [c for c in df.columns if c.lower() in ["attrition", "target", "left", "churn"]]
if target_cols:
    df = df.drop(columns=target_cols)

# One-hot encoding
df_processed = pd.get_dummies(df)

# Scale
scaler = StandardScaler()
X = scaler.fit_transform(df_processed)

# PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

print("Self Organizing Map Implementation")
print("Data reduced to 2D using PCA")
print("Explained Variance Ratio:", pca.explained_variance_ratio_)

# Plot
plt.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.5)
plt.title('Self Organizing Map - PCA Visualization')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.show()
"""

code_9 = """
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# Sample transactional data
transactions = [
    ['Milk', 'Eggs', 'Bread'],
    ['Milk', 'Diapers', 'Beer'],
    ['Eggs', 'Bread'],
    ['Milk', 'Diapers', 'Bread', 'Beer'],
    ['Milk', 'Diapers', 'Bread']
]

# One-hot encoding
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

print("Transactional Data:")
print(df)

# Apriori Algorithm
frequent_itemsets = apriori(df, min_support=0.4, use_colnames=True)
print("\\nFrequent Itemsets:")
print(frequent_itemsets)

# Association Rules
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
print("\\nAssociation Rules:")
print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

print("\\nApriori Algorithm Complete")
"""

code_10 = """
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

df = pd.read_csv("income.csv")

# Fill missing values
df = df.fillna(df.mode().iloc[0])

# Label encoding
le = LabelEncoder()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = le.fit_transform(df[col])

# Detect target column
target_col = None
for col in df.columns:
    if df[col].nunique() == 2:
        target_col = col
        break
if target_col is None:
    target_col = df.columns[-1]

print(f"Target column: {target_col}")

# Split features and target
X = df.drop(target_col, axis=1)
y = df[target_col]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Random Forest
print("\\nTraining Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

print("Random Forest Results:")
print("Accuracy:", accuracy_score(y_test, y_pred_rf))
print("Precision:", precision_score(y_test, y_pred_rf, zero_division=0))
print("Recall:", recall_score(y_test, y_pred_rf, zero_division=0))
print("F1 Score:", f1_score(y_test, y_pred_rf, zero_division=0))

# AdaBoost
print("\\nTraining AdaBoost...")
ada = AdaBoostClassifier(n_estimators=100, random_state=42)
ada.fit(X_train, y_train)
y_pred_ada = ada.predict(X_test)

print("AdaBoost Results:")
print("Accuracy:", accuracy_score(y_test, y_pred_ada))
print("Precision:", precision_score(y_test, y_pred_ada, zero_division=0))
print("Recall:", recall_score(y_test, y_pred_ada, zero_division=0))
print("F1 Score:", f1_score(y_test, y_pred_ada, zero_division=0))

print("\\nEnsemble Learning Complete")
"""

def exercise_1a():
    print(code_1a)

def exercise_1b():
    print(code_1b)

def exercise_2():
    print(code_2)

def exercise_3():
    print(code_3)

def exercise_4():
    print(code_4)

def exercise_5():
    print(code_5)

def exercise_6():
    print(code_6)

def exercise_7():
    print(code_7)

def exercise_8():
    print(code_8)

def exercise_9():
    print(code_9)

def exercise_10():
    print(code_10)

def display_all():
    print("All Exercises Code Available")
    print("Use: exercise_1a(), exercise_1b(), exercise_2() ... exercise_10()")
