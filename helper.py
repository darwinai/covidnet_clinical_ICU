import pandas as pd
import tensorflow as tf
from tensorflow.python.platform import gfile
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
import numpy as np
TOTAL_NUMBER_OF_RECORDS = 1925
RECORDS_PER_PATIENT = 5
TEST_SAMPLES = 423

def load_model(model_name):
    graph_def = tf.GraphDef()
    with gfile.FastGFile(model_name, 'rb') as f:
        # Parses a serialized binary message into the current message.
        graph_def.ParseFromString(f.read())

    sess = tf.Session()
    
    # Import a serialized TensorFlow `GraphDef` protocol buffer
    # and place into the current default `Graph`.
    tf.import_graph_def(graph_def)
    return sess

def print_results(sess, train_x, test_x, train_y, test_y):
    input_tensor = sess.graph.get_tensor_by_name("import/dense_1_input:0")
    output_tensor = tf.get_default_graph().get_tensor_by_name("import/dense_5/Sigmoid:0")
    dic = {input_tensor:test_x}

    y_pred_test = sess.run(output_tensor, dic)
    y_pred_test[y_pred_test>0.5] = 1
    y_pred_test[y_pred_test<=0.5] = 0

    dic = {input_tensor:train_x}
    y_pred_train = sess.run(output_tensor, dic)
    y_pred_train[y_pred_train>0.5] = 1
    y_pred_train[y_pred_train<=0.5] = 0
    accuracy = accuracy_score(test_y.astype(np.int64), y_pred_test)
    print('Accuracy:', accuracy)
    predictions = y_pred_test.reshape(TEST_SAMPLES).astype(np.uint32)
    labels = test_y.astype(np.uint32)
    accuracy = np.sum(labels == predictions) /TEST_SAMPLES

    positive_index = np.where(predictions == 1) 
    negative_index = np.where(predictions == 0) 

    TP_index = np.where(labels[positive_index] == predictions[positive_index])[0]
    TN_index = np.where(labels[negative_index] == predictions[negative_index])[0]
    FP_index = np.where(labels[positive_index] != predictions[positive_index])[0]
    FN_index = np.where(labels[negative_index] != predictions[negative_index])[0]
    
    Accuracy = (TP_index.shape[0] + TN_index.shape[0])/TEST_SAMPLES # 
    Sensitivity = TP_index.shape[0] / (TP_index.shape[0] + FN_index.shape[0]) # Sensitivity
    Specificity = TN_index.shape[0] / (FP_index.shape[0] + TN_index.shape[0]) # Specificity
    print("TP: {} TN: {} FP: {} FN: {}".format(TP_index.shape[0], TN_index.shape[0], FP_index.shape[0], FN_index.shape[0]))
    print("Accuracy: {} Sensitivity: {} Specificity: {}\n".format(Accuracy, Sensitivity, Specificity))
    
    
def load_and_process_features():
    # Read data
    raw_data = pd.read_excel('Kaggle_Sirio_Libanes_ICU_Prediction.xls')

    # Data Preparation
    raw_data['AGE_PERCENTIL'] = raw_data['AGE_PERCENTIL'].str.replace('Above ','').str.extract(r'(.+?)th')
    raw_data['WINDOW'] = raw_data['WINDOW'].str.replace('ABOVE_12','12-more').str.extract(r'(.+?)-')

    # Replace nan with -2
    mean_impute  = SimpleImputer(strategy='constant', fill_value = -2)
    imputed_data = mean_impute.fit_transform(raw_data)
    imputed_data = pd.DataFrame(imputed_data, columns = raw_data.columns)

    for i in range(int(TOTAL_NUMBER_OF_RECORDS/5)):
        # provide label for instances with ICU = 0
        label = np.max(imputed_data["ICU"][i*RECORDS_PER_PATIENT:(i+1)*RECORDS_PER_PATIENT])
        if label == 1:
            for index in range(RECORDS_PER_PATIENT):
                # if the patient is already at ICU then we set the label to 2 so in the feature we remove this record
                if imputed_data["ICU"][i*RECORDS_PER_PATIENT+ index] == 1:
                    imputed_data["ICU"][i*RECORDS_PER_PATIENT+ index] = 2
                else:
                    imputed_data["ICU"][i*RECORDS_PER_PATIENT+ index] = 1

        # replace missing values of each patient by values from previous time window
        for col in imputed_data.columns:
            last_value = imputed_data[col][i*RECORDS_PER_PATIENT]
            last_index = i*RECORDS_PER_PATIENT
            for k in [1, 2, 3, 4]:
                if (imputed_data[col][i*RECORDS_PER_PATIENT + k] == -2) :
                    imputed_data[col][i*RECORDS_PER_PATIENT + k] = last_value
                else:
                    if last_value == -2:
                        for index in range(k):
                            if imputed_data[col][i*5 + index] == -2: 
                                imputed_data[col][i*5 + index] = imputed_data[col][i*5 + k]
                    last_value = imputed_data[col][i*5 + k]

    # remove the records of patients who have been addmited to ICU
    imputed_data = imputed_data[imputed_data.ICU != 2]    
    # We dont need Window column any more
    imputed_data.drop([ 'WINDOW'], inplace=True, axis=1)

    x_grouped = imputed_data.copy()
    y = x_grouped.ICU
    x_grouped.drop(['PATIENT_VISIT_IDENTIFIER', 'ICU'], inplace=True, axis=1)
    
    return x_grouped, y
