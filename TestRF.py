import pandas as pd
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def data_standardization(df_input):
    sc = StandardScaler()   
    df=sc.fit_transform(df_input)
    return df

warnings.filterwarnings('ignore')

#Read data
data = pd.read_csv('data/project1_train.csv')
test = pd.read_csv('data/project1_test.csv')
#data = data.drop([29, 60, 297, 347])
#des = data.describe()
#des2 = test.describe()

#Outliers
from scipy.stats import boxcox
out = ['Alkaline_Phosphotase', 'Alamine_Aminotransferase', 'Aspartate_Aminotransferase'] 
for i in out:
    #transform_data = data[i]**(1/3)
    #transform_data2 = test[i]**(1/3)
    transform_data, lam = boxcox(data[i])
    transform_data2, lam = boxcox(test[i])
    for j in range(0, data.shape[0]):
        data.loc[j, i] = transform_data[j]
    for j in range(0, test.shape[0]):
        test.loc[j, i] = transform_data2[j]
#des = data.describe()
#des2 = test.describe()

#Revise Male, Female
data.loc[data.Gender=='Male', 'Gender'] = 1
data.loc[data.Gender=='Female', 'Gender'] = 0
test.loc[test.Gender=='Male', 'Gender'] = 1
test.loc[test.Gender=='Female', 'Gender'] = 0

from sklearn.impute import SimpleImputer
# 建立以平均值填補缺損值的實體
imp = SimpleImputer(strategy='most_frequent')  #mean, median, most_frequent
# 填補缺損值
imp.fit(data)
data2 = imp.transform(data)
data = pd.DataFrame(data2, index = data.index, columns = data.columns)

#Standardization
X_df = data_standardization(data.iloc[:,0:10])
y_df = data['Label'].astype('int')
test = data_standardization(test)

#Dvide the data into validation and test sets
X_train , X_test , y_train , y_test = train_test_split(X_df ,y_df , test_size=0.3 , random_state=408570344)

'''
#crossvalidator
from sklearn.model_selection import KFold
KFold(n_splits=2, random_state=408570344, shuffle=False)
'''

#Random Forest
from sklearn.ensemble import RandomForestClassifier
params = { 'criterion': ["gini", "entropy", "log_loss"],
#           'splitter': ["best", "random"],
           'min_samples_leaf': [1, 3, 6, 10],
           'max_depth': [1, 3, 6, 10],
           'n_estimators': [100, 500, 1000]}
'''
from sklearn.model_selection import GridSearchCV
model = RandomForestClassifier()
clf = GridSearchCV(estimator = model,
                   param_grid = params,
                   scoring = 'neg_mean_squared_error',
                   verbose = 1,
                   cv = 10)
clf.fit(X_train, y_train)

print("Best parameters:", clf.best_params_)
print(clf.best_estimator_)
#Best parameters: {'criterion': 'gini', 'max_depth': 10, 'min_samples_leaf': 3, 'n_estimators': 500}
#RandomForestClassifier(max_depth=10, min_samples_leaf=3, n_estimators=500)
'''
'''
dt_params = { 'criterion': "gini",
           'splitter': "random",
           'min_samples_leaf': 1,
           'max_depth': 1}
'''
#model = clf.best_estimator_
model = RandomForestClassifier(max_depth=10, min_samples_leaf=3, n_estimators=500)
model.fit(X_train, y_train)

from sklearn.metrics import accuracy_score
y_pred = model.predict(X_test)
print('XGBoost model accuracy score: {0:0.4f}'. format(accuracy_score(y_test, y_pred))) #0.6809

#Output predict data
result = pd.DataFrame([], columns=['Id', 'Category'])
result['Id'] = [f'{i:03d}' for i in range(len(test))]
result['Category'] = model.predict(test).astype(int)
result.to_csv("data/predict.csv", index = False) #0.69565
