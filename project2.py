# Import necessary tools
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report

# 1. Load the Dataset
# X contains the 4 flower measurements, y contains the species labels
iris = load_iris()
X = iris.data
y = iris.target

# 2. Split the Dataset (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. The Gatekeeper: Feature Scaling
# We fit the scaler ONLY on the training data to prevent data leakage, 
# then apply that same scale to both train and test sets.
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Apply the KNN Algorithm (Supervised Learning)
# We set k=5 neighbors and train (fit) the model using the scaled data and known answers.
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)

# 5. Make Predictions
# We hand the model the scaled test data (measurements only) and ask it to guess the species.
y_pred = knn.predict(X_test_scaled)

# 6. Build the Confusion Matrix
# We compare the model's guesses (y_pred) against the actual correct answers (y_test).
cm = confusion_matrix(y_test, y_pred)

print("Confusion Matrix:")
print(cm)

print("\nDetailed Diagnostic Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))