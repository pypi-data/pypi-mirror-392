def linear_regression():
    """
    #linear regression
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, r2_score
    
    data = pd.DataFrame({
        'Hours':[1,2,3,4.5,5,6,7,8.5,9,10],
        'Marks':[35,40,50,60,62,70,75,85,88,95]
    })
    
    X = data[['Hours']]
    y = data['Marks']
    
    m = LinearRegression().fit(X, y)
    yp = m.predict(X)
    
    print("Intercept:", round(m.intercept_,2))
    print("Slope:", round(m.coef_[0],2))
    print("MSE:", round(mean_squared_error(y, yp),2))
    print("R2:", round(r2_score(y, yp),2))
    
    print("Predicted for 6.5:", round(m.predict([[6.5]])[0],2))
    
    plt.scatter(X, y)
    plt.plot(X, yp)
    plt.show()

    """
    pass
    

def ROC_AUC():
    """
    #roc_auc
    import numpy as np
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, roc_auc_score
    from sklearn.preprocessing import label_binarize
    import matplotlib.pyplot as plt
    
    iris = load_iris()
    X, y, names = iris.data, iris.target, iris.target_names
    
    # --- Binary Logistic Regression (0 vs 1) ---
    mask = y < 2
    Xb, yb = X[mask], y[mask]
    bin_model = LogisticRegression().fit(Xb, yb)
    p = bin_model.predict(Xb)
    prob = bin_model.predict_proba(Xb)[:,1]
    
    print(confusion_matrix(yb, p))
    print(classification_report(yb, p, target_names=names[:2]))
    
    fpr, tpr, _ = roc_curve(yb, prob)
    plt.plot(fpr, tpr, label=f"AUC={auc(fpr,tpr):.2f}")
    plt.plot([0,1],[0,1],'k--')
    plt.legend(); plt.show()
    
    # --- Multiclass Logistic Regression ---
    multi = LogisticRegression(multi_class='ovr', solver='liblinear').fit(X, y)
    pm = multi.predict(X)
    probm = multi.predict_proba(X)
    ybm = label_binarize(y, classes=[0,1,2])
    
    print(confusion_matrix(y, pm))
    print(classification_report(y, pm, target_names=names))
    
    for i in range(3):
        fpr, tpr, _ = roc_curve(ybm[:,i], probm[:,i])
        plt.plot(fpr, tpr, label=f"{names[i]} AUC={auc(fpr,tpr):.2f}")
    plt.plot([0,1],[0,1],'k--')
    plt.legend(); plt.show()

    """
    pass
    

def multivariate_logistic_regression():
    """
    # Import necessary libraries
    import pandas as pd
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Step 1: Load the Iris dataset
    iris = load_iris()
    X = iris.data  # Features (sepal and petal length/width)
    y = iris.target  # Target classes (0=setosa, 1=versicolor, 2=virginica)
    
    # Step 2: Multiclass Logistic Regression (using all 3 classes)
    multi_model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=200)
    multi_model.fit(X, y)
    y_pred_multi = multi_model.predict(X)
    
    # Step 3: Evaluate Multiclass Model
    print("=== Multiclass Logistic Regression===")
    print(f"Accuracy: {accuracy_score(y, y_pred_multi) * 100:.2f}%")
    print("Classification Report:")
    print(classification_report(y, y_pred_multi, target_names=iris.target_names))
    
    # Step 4: Visualize Confusion Matrix
    cm_multi = confusion_matrix(y, y_pred_multi)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm_multi, annot=True, cmap='Blues', fmt='d',
                xticklabels=iris.target_names, yticklabels=iris.target_names)
    plt.title("Multiclass Logistic Regression Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig("iris_multiclass_confusion.png")
    plt.show()
    
    # Step 5: Binary Logistic Regression (only class 0 vs 1)
    # Filter only setosa and versicolor
    binary_filter = y < 2
    X_binary = X[binary_filter]
    y_binary = y[binary_filter]
    
    binary_model = LogisticRegression(solver='lbfgs')
    binary_model.fit(X_binary, y_binary)
    y_pred_binary = binary_model.predict(X_binary)
    
    # Step 6: Evaluate Binary Model
    print("\n=== Binary Logistic Regression (Setosa vs Versicolor)===")
    print(f"Accuracy: {accuracy_score(y_binary, y_pred_binary) * 100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_binary, y_pred_binary, target_names=iris.target_names[:2]))
    
    # Step 7: Binary Confusion Matrix
    cm_binary = confusion_matrix(y_binary, y_pred_binary)
    plt.figure(figsize=(4,3))
    sns.heatmap(cm_binary, annot=True, cmap='Greens', fmt='d',
                xticklabels=iris.target_names[:2], yticklabels=iris.target_names[:2])
    plt.title("Binary Logistic Regression Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig("iris_binary_confusion.png")
    plt.show()
    """
    pass
    

def knn():
    """
    #knn
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import confusion_matrix, classification_report
    
    iris = load_iris(as_frame=True)
    df = iris.frame
    df["species"] = df["target"].map(dict(enumerate(iris.target_names)))
    
    X = df.drop(columns=["target", "species"])
    y = df["species"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train = StandardScaler().fit_transform(X_train)
    X_test = StandardScaler().fit_transform(X_test)
    
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    pred = knn.predict(X_test)
    
    print(classification_report(y_test, pred))
    cm = confusion_matrix(y_test, pred)
    
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=knn.classes_, yticklabels=knn.classes_)
    plt.show()
    """
    pass

def decisiontree():
    """
    #decision tree
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    from sklearn.preprocessing import LabelEncoder
    import matplotlib.pyplot as plt
    
    
    df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    df = df[['Pclass','Sex','Age','Fare','Embarked','Survived']]
    df['Age'] = df['Age'].fillna(df['Age'].median())
    df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])
    
    
    for c in ['Sex','Embarked']:
        df[c] = LabelEncoder().fit_transform(df[c])
    
    X = df[['Pclass','Sex','Age','Fare','Embarked']]
    y = df['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = DecisionTreeClassifier().fit(X_train, y_train)
    print(clf.score(X_test, y_test))
    
    plot_tree(clf, feature_names=X.columns, filled=True)
    plt.show()
    """
    pass

def svm():
    """
    #SVM
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn import datasets
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score
    
    # Data
    iris = datasets.load_iris()
    X, y = iris.data[:, 2:4], iris.target
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    
    # Scale
    sc = StandardScaler()
    Xtr = sc.fit_transform(Xtr)
    Xte = sc.transform(Xte)
    
    # Train 3 SVMs
    kernels = ["linear", "poly", "rbf"]
    models = {k: SVC(kernel=k, gamma="auto").fit(Xtr, ytr) for k in kernels}
    
    # Accuracy
    for k in kernels:
        print(k, accuracy_score(yte, models[k].predict(Xte)))
    
    # Plot boundary
    def draw(m, X, y, title):
        xx, yy = np.meshgrid(
            np.linspace(X[:,0].min()-1, X[:,0].max()+1, 300),
            np.linspace(X[:,1].min()-1, X[:,1].max()+1, 300)
        )
        Z = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        plt.contourf(xx, yy, Z, alpha=.4)
        plt.scatter(X[:,0], X[:,1], c=y)
        plt.title(title)
        plt.show()
    
    for k in kernels:
        draw(models[k], Xte, yte, k.upper())

    """
    pass

def logistic_decision_boundary():
    """
    #2d logistic regression
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    
    X, y = make_classification(n_samples=200, n_features=2, n_redundant=0,
                               n_clusters_per_class=1, class_sep=1.5, random_state=42)
    
    X = StandardScaler().fit_transform(X)
    m = LogisticRegression().fit(X, y)
    
    xx, yy = np.meshgrid(
        np.linspace(X[:,0].min()-1, X[:,0].max()+1, 300),
        np.linspace(X[:,1].min()-1, X[:,1].max()+1, 300)
    )
    
    Z = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    
    plt.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
    plt.scatter(X[:,0], X[:,1], c=y, cmap='coolwarm')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.show()

    """
    pass

def binary_logistic_regression():
    """
    # Import required libraries
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Step 1: Create dataset
    # Marks < 50 = Fail (0), Marks >= 50 = Pass (1)
    data = pd.DataFrame({
        'Marks': [25, 35, 45, 50, 55, 60, 65, 70, 80, 85, 90, 95],
        'Result': [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    })
    
    # Step 2: Features and labels
    X = data[['Marks']]  # Feature matrix
    y = data['Result']   # Labels
    
    # Step 3: Train logistic regression model
    model = LogisticRegression()
    model.fit(X, y)
    
    # Step 4: Model predictions on training data
    y_pred = model.predict(X)
    
    # Step 5: Predict on a test case (e.g., 58 marks)
    test_marks = [[58]]
    test_pred = model.predict(test_marks)
    test_prob = model.predict_proba(test_marks)[0][1]  # Probability of passing
    
    print(f"Test Marks: 58")
    print(f"Predicted Class: {'Pass' if test_pred[0] == 1 else 'Fail'}")
    print(f"Predicted Probability of Passing: {test_prob:.2f}")
    
    # Step 6: Evaluate model
    acc = accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred)
    print(f"\nAccuracy: {acc*100:.2f}%")
    print("Confusion Matrix:")
    print(cm)
    
    # Step 7: Plot logistic curve with test point
    x_vals = np.linspace(20, 100, 200).reshape(-1, 1)
    y_probs = model.predict_proba(x_vals)[:, 1]
    
    plt.figure(figsize=(8,5))
    plt.scatter(X, y, color='blue', label='Training Data (Pass/Fail)')
    plt.plot(x_vals, y_probs, color='red', label='Logistic Curve')
    plt.axhline(0.5, linestyle='--', color='gray', label='Decision Threshold')
    plt.scatter(test_marks, test_prob, color='green', s=100, label='Test (58 marks)')
    plt.title('Logistic Regression: Marks vs Pass Probability')
    plt.xlabel('Marks')
    plt.ylabel('Probability of Passing')
    plt.legend()
    plt.grid(True)
    plt.savefig('logistic_pass_fail.png')
    plt.show()
    
    # Step 8: Plot confusion matrix
    plt.figure(figsize=(4,4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Fail', 'Pass'], yticklabels=['Fail', 'Pass'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig('confusion_matrix.png')
    plt.show()
    """
    pass
    

def pca():
    """
    #PCA
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    from sklearn.datasets import load_digits
    
    X, y = load_digits(return_X_y=True)
    print("Original:", X.shape)
    
    p = PCA(2)
    X2 = p.fit_transform(X)
    print("Reduced:", X2.shape)
    print("Var:", p.explained_variance_ratio_)
    
    plt.scatter(X2[:,0], X2[:,1], c=y, cmap='tab10')
    plt.title("PCA 64D → 2D")
    plt.show()
    
    pfull = PCA().fit(X)
    plt.plot(np.cumsum(pfull.explained_variance_ratio_))
    
    plt.title("Scree Plot")
    plt.show()
    """
    pass

def random_forest():
    """
    #random forest
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, confusion_matrix
    
    df=pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    cols=["Pclass","Sex","Age","Fare","Embarked"]
    df=df[cols + ["Survived"]]
    
    #handle missing values
    df["Age"].fillna(df["Age"].median(),inplace=True)
    df["Embarked"].fillna(df["Embarked"].mode()[0],inplace=True)
    
    for c in ["Sex","Embarked"]:
        df[c]=LabelEncoder().fit_transform(df[c])
    X=df[cols]
    y=df["Survived"]
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42)
    
    dt=DecisionTreeClassifier().fit(Xtr,ytr)
    rf=RandomForestClassifier(n_estimators=100, random_state=42).fit(Xtr,ytr)
    
    dtp=dt.predict(Xte)
    rfp=rf.predict(Xte)
    
    print("DT:", accuracy_score(yte, dtp))
    print("RF:",accuracy_score(yte,rfp))
    
    pd.Series(rf.feature_importances_, index=cols).plot.barh()
    plt.show()
    
    fig, ax =plt.subplots(1,2,figsize=(8,4))
    ax[0].imshow(confusion_matrix(yte,dtp)); 
    ax[0].set_title("DT")
    ax[1].imshow(confusion_matrix(yte, rfp))
    ax[1].set_title("RF")
    plt.show()
    """
    pass

def  adaboost_vs_randomf_vs_gradient():
    '''
    #adaboost vs random forest vs GB
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
    
    df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    
    features = ['Pclass','Sex','Age','Fare','Embarked']
    df = df[features + ['Survived']]
    df.Age.fillna(df.Age.median(), inplace=True)
    df.Embarked.fillna(df.Embarked.mode()[0], inplace=True)
    
    for c in ['Sex','Embarked']:
        df[c] = LabelEncoder().fit_transform(df[c])
    
    X, y = df[features], df['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        "RF": RandomForestClassifier(n_estimators=100, random_state=42),
        "AdaBoost": AdaBoostClassifier(n_estimators=100, random_state=42),
        "GB": GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    labels, f1_scores = [], []
    for name, m in models.items():
        m.fit(X_train, y_train)
        pred = m.predict(X_test)
        labels.append(name)
        f1_scores.append(f1_score(y_test, pred))
        print(f"{name}  Acc:{accuracy_score(y_test,pred):.2f}  F1:{f1_score(y_test,pred):.2f}")
    
    plt.bar(labels, f1_scores)
    plt.ylabel("F1 Score")
    plt.title("Model Comparison")
    plt.show()

    '''
    pass
    
def L1_vs_L2():
    '''    
    #L1/L2
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score
    
    # Data
    X, y = make_classification(n_samples=500, n_features=10, n_informative=2, random_state=42)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)
    sc = StandardScaler()
    Xtr, Xte = sc.fit_transform(Xtr), sc.transform(Xte)
    
    def eval_model(penalty, C, title):
        m = LogisticRegression(penalty=penalty, C=C, solver='liblinear').fit(Xtr, ytr)
        print(title, "Acc=", round(accuracy_score(yte, m.predict(Xte)), 2))
    
        # plot (only 2 features)
        x1, x2 = Xte[:,0], Xte[:,1]
        xx, yy = np.meshgrid(np.linspace(x1.min()-1, x1.max()+1, 300),
                             np.linspace(x2.min()-1, x2.max()+1, 300))
        grid = np.zeros((xx.size, Xtr.shape[1]))
        grid[:, :2] = np.c_[xx.ravel(), yy.ravel()]
        Z = m.predict(grid).reshape(xx.shape)
    
        plt.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
        plt.scatter(x1, x2, c=yte, cmap='coolwarm', edgecolor='k')
        plt.title(title); plt.show()
    
    eval_model('l2', 0.01, "L2 C=0.01")
    eval_model('l2', 1,    "L2 C=1")
    eval_model('l2', 100,  "L2 C=100")
    eval_model('l1', 1,    "L1 C=1")
    
    '''
    pass
    
def feature_imp_ensemble():
    '''
    #trains three ensemble machine-learning models on the Titanic dataset and compares their feature importances
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
    
    df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    
    features = ['Pclass','Sex','Age','Fare','Embarked']
    df = df[features + ['Survived']]
    df.Age.fillna(df.Age.median(), inplace=True)
    df.Embarked.fillna(df.Embarked.mode()[0], inplace=True)
    
    for col in ['Sex','Embarked']:
        df[col] = LabelEncoder().fit_transform(df[col])
    
    X, y = df[features], df['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    importance_df = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        importance_df.append(pd.DataFrame({
            'Feature': features,
            'Importance': model.feature_importances_,
            'Model': name
        }))
    
    importance_df = pd.concat(importance_df)
    
    sns.barplot(data=importance_df, x='Importance', y='Feature', hue='Model')
    plt.title('Feature Importance Comparison')
    plt.show()

    '''
    pass
    
def three_layer_mlp():
    
    '''
    # Import libraries
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.datasets import make_moons
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    # Step 1: Generate synthetic binary classification data
    X, y = make_moons(n_samples=1000, noise=0.2, random_state=42)
    y = y.reshape(-1, 1)  # Reshape for matrix operations
    
    # Step 2: Split and scale
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Step 3: Define activation functions and derivatives
    def sigmoid(z):
        return 1 / (1 + np.exp(-z))
    
    def sigmoid_derivative(a):
        return a * (1 - a)
    
    def relu(z):
        return np.maximum(0, z)
    
    def relu_derivative(z):
        return (z > 0).astype(float)
    
    # Step 4: Initialize weights and biases
    input_dim = X_train.shape[1]  # 2
    hidden_dim = 10
    output_dim = 1
    
    np.random.seed(42)
    W1 = np.random.randn(input_dim, hidden_dim) * 0.1
    b1 = np.zeros((1, hidden_dim))
    W2 = np.random.randn(hidden_dim, output_dim) * 0.1
    b2 = np.zeros((1, output_dim))
    
    # Step 5: Training parameters
    learning_rate = 0.1
    epochs = 1000
    losses = []
    
    # Step 6: Training loop
    for epoch in range(epochs):
        # Forward pass
        Z1 = X_train @ W1 + b1
        A1 = relu(Z1)
        Z2 = A1 @ W2 + b2
        A2 = sigmoid(Z2)
    
        # Compute loss (binary cross-entropy)
        m = y_train.shape[0]
        loss = -np.mean(y_train * np.log(A2 + 1e-8) + (1 - y_train) * np.log(1 - A2 + 1e-8))
        losses.append(loss)
    
        # Backward pass
        dZ2 = A2 - y_train
        dW2 = A1.T @ dZ2 / m
        db2 = np.sum(dZ2, axis=0, keepdims=True) / m
    
        dA1 = dZ2 @ W2.T
        dZ1 = dA1 * relu_derivative(Z1)
        dW1 = X_train.T @ dZ1 / m
        db1 = np.sum(dZ1, axis=0, keepdims=True) / m
    
        # Update weights and biases
        W1 -= learning_rate * dW1
        b1 -= learning_rate * db1
        W2 -= learning_rate * dW2
        b2 -= learning_rate * db2
    
        # Print loss occasionally
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss:.4f}")
    
    # Step 7: Evaluate on test set
    Z1_test = X_test @ W1 + b1
    A1_test = relu(Z1_test)
    Z2_test = A1_test @ W2 + b2
    A2_test = sigmoid(Z2_test)
    y_pred = (A2_test > 0.5).astype(int)
    accuracy = np.mean(y_pred == y_test)
    print(f"Test Accuracy: {accuracy:.2f}")
    
    # Step 8: Plot decision boundary
    def plot_decision_boundary(pred_func, X, y):
        x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
        y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5
        h = 0.02
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        grid = np.c_[xx.ravel(), yy.ravel()]
        grid_scaled = scaler.transform(grid)
        Z1 = grid_scaled @ W1 + b1
        A1 = relu(Z1)
        Z2 = A1 @ W2 + b2
        A2 = sigmoid(Z2)
        preds = (A2 > 0.5).astype(int).reshape(xx.shape)
    
        plt.figure(figsize=(6, 5))
        plt.contourf(xx, yy, preds, cmap=plt.cm.coolwarm, alpha=0.6)
        plt.scatter(X[:, 0], X[:, 1], c=y.ravel(), cmap=plt.cm.coolwarm, edgecolors='k')
        plt.title("MLP Decision Boundary (NumPy)")
        plt.tight_layout()
        plt.show()
    
    plot_decision_boundary(None, X, y)
    '''
    pass
    
def shallow_deep_nn():
    
    '''
    # Shallow vs Deep Neural Network on MNIST
    import tensorflow as tf
    from tensorflow.keras.datasets import mnist
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Flatten, Dropout
    from tensorflow.keras.utils import to_categorical
    import matplotlib.pyplot as plt
    import numpy as np
    
    # --------------------------#
    # Step 1: Load and preprocess MNIST data
    # --------------------------#
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    # Normalize pixel values (0-255 → 0-1)
    x_train = x_train.astype('float32') / 255.0
    x_test = x_test.astype('float32') / 255.0
    
    # One-hot encode labels
    y_train = to_categorical(y_train, 10)
    y_test = to_categorical(y_test, 10)
    
    # --------------------------#
    # Step 2: Define Shallow Neural Network (1 hidden layer)
    # --------------------------#
    shallow_model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])
    
    shallow_model.compile(optimizer='adam',
                          loss='categorical_crossentropy',
                          metrics=['accuracy'])
    
    # --------------------------#
    # Step 3: Define Deep Neural Network (3 hidden layers)
    # --------------------------#
    deep_model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(512, activation='relu'),
        Dropout(0.3),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])
    
    deep_model.compile(optimizer='adam',
                       loss='categorical_crossentropy',
                       metrics=['accuracy'])
    
    # --------------------------#
    # Step 4: Train both models
    # --------------------------#
    print("Training Shallow Network...")
    history_shallow = shallow_model.fit(
        x_train, y_train,
        epochs=10,
        batch_size=128,
        validation_split=0.1,
        verbose=2
    )
    
    print("\nTraining Deep Network...")
    history_deep = deep_model.fit(
        x_train, y_train,
        epochs=10,
        batch_size=128,
        validation_split=0.1,
        verbose=2
    )
    
    # --------------------------#
    # Step 5: Evaluate models on test data
    # --------------------------#
    test_loss_shallow, test_acc_shallow = shallow_model.evaluate(x_test, y_test, verbose=0)
    test_loss_deep, test_acc_deep = deep_model.evaluate(x_test, y_test, verbose=0)
    
    print("\n===== Performance Comparison =====")
    print(f"Shallow Network Test Accuracy: {test_acc_shallow:.4f}")
    print(f"Deep Network Test Accuracy: {test_acc_deep:.4f}")
    
    # --------------------------#
    # Step 6: Plot training curves
    # --------------------------#
    plt.figure(figsize=(12, 5))
    
    # Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history_shallow.history['accuracy'], label='Shallow Train Acc')
    plt.plot(history_shallow.history['val_accuracy'], label='Shallow Val Acc')
    plt.plot(history_deep.history['accuracy'], label='Deep Train Acc')
    plt.plot(history_deep.history['val_accuracy'], label='Deep Val Acc')
    plt.title('Training vs Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    
    # Loss
    plt.subplot(1, 2, 2)
    plt.plot(history_shallow.history['loss'], label='Shallow Train Loss')
    plt.plot(history_shallow.history['val_loss'], label='Shallow Val Loss')
    plt.plot(history_deep.history['loss'], label='Deep Train Loss')
    plt.plot(history_deep.history['val_loss'], label='Deep Val Loss')
    plt.title('Training vs Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    '''
    pass

def dropout_batch_norm():
    '''
    import os
    import warnings
    warnings.filterwarnings('ignore')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    import numpy as np
    import matplotlib.pyplot as plt
    from tensorflow.keras.datasets import mnist
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Flatten, Dropout, BatchNormalization
    from tensorflow.keras.utils import to_categorical
    from tensorflow.keras.optimizers import Adam
    
    # Step 1: Load and preprocess MNIST data
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0
    y_train_cat = to_categorical(y_train, 10)
    y_test_cat = to_categorical(y_test, 10)
    
    # Step 2: Build deep model with Dropout + Batch Normalization
    model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(10, activation='softmax')
    ])
    
    # Step 3: Compile the model
    model.compile(optimizer=Adam(),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    # Step 4: Train the model
    history = model.fit(x_train, y_train_cat,
                        epochs=15,
                        batch_size=128,
                        validation_split=0.2,
                        verbose=1)
    
    # Step 5: Evaluate on test set
    test_loss, test_acc = model.evaluate(x_test, y_test_cat, verbose=0)
    print(f"Test Accuracy with Dropout + BatchNorm: {test_acc:.4f}")
    
    # Step 6: Plot training history
    def plot_history(hist):
        plt.figure(figsize=(12, 5))
    
        # Accuracy
        plt.subplot(1, 2, 1)
        plt.plot(hist.history['accuracy'], label='Train Accuracy')
        plt.plot(hist.history['val_accuracy'], label='Val Accuracy')
        plt.title("Model Accuracy")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.legend()
        plt.grid(True)
    
        # Loss
        plt.subplot(1, 2, 2)
        plt.plot(hist.history['loss'], label='Train Loss')
        plt.plot(hist.history['val_loss'], label='Val Loss')
        plt.title("Model Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        plt.grid(True)
    
        plt.tight_layout()
        plt.savefig("mnist_dropout_batchnorm.png")
        plt.show()
    
    plot_history(history)
    '''
    pass
    
def handwritten_digit_classi():
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    from tensorflow.keras.datasets import mnist
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Flatten, Dropout
    from tensorflow.keras.utils import to_categorical
    from tensorflow.keras.optimizers import Adam
    
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0
    
    y_train_cat = to_categorical(y_train, 10)
    y_test_cat = to_categorical(y_test, 10)
    
    model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(512, activation='relu'),
        Dropout(0.2),
        Dense(256, activation='relu'),
        Dropout(0.2),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])
    
    model.compile(optimizer=Adam(),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    history = model.fit(x_train, y_train_cat,
                        epochs=10,
                        batch_size=128,
                        validation_split=0.2,
                        verbose=1)
    
    test_loss, test_acc = model.evaluate(x_test, y_test_cat, verbose=0)
    print("Test Accuracy:", test_acc)
    
    def plot_history(hist):
        plt.figure(figsize=(12, 5))
    
        plt.subplot(1, 2, 1)
        plt.plot(hist.history['accuracy'], label='Train Acc')
        plt.plot(hist.history['val_accuracy'], label='Val Acc')
        plt.title("Accuracy")
        plt.xlabel("Epoch"); plt.ylabel("Acc")
        plt.legend(); plt.grid(True)
    
        plt.subplot(1, 2, 2)
        plt.plot(hist.history['loss'], label='Train Loss')
        plt.plot(hist.history['val_loss'], label='Val Loss')
        plt.title("Loss")
        plt.xlabel("Epoch"); plt.ylabel("Loss")
        plt.legend(); plt.grid(True)
    
        plt.tight_layout()
        plt.show()
    
    plot_history(history)

    '''
    pass