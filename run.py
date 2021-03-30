from sklearn.model_selection import train_test_split
import tensorflow as tf
import pickle


from helper import load_and_process_features, print_results, load_model
import numpy as np

##Load Data and Preprocessing
features, labels = load_and_process_features()

# Split data into test and train set
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state = 0)

# include only quantitatively positive impact clinical features
negative_impact_features = pickle.load( open( "negative_impact_features.pkl", "rb" ) )
for feature in negative_impact_features:
    del X_train[feature]
    del X_test[feature]
train_x = X_train.to_numpy().astype(np.float)
test_x = X_test.to_numpy().astype(np.float)
train_y = y_train.to_numpy().astype(np.float)
test_y = y_test.to_numpy().astype(np.float)

sess = load_model("models/covidnet_icu.pb")
print_results(sess, train_x, test_x, train_y, test_y)
