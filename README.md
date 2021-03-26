# covidnet_clinical_ICU
Open Source project to help predict ICU admission from clinical data. 

# Dataset #


Dataset has 1925 records from 385 patients. For each patients we have 5 records for 5 different time windows:

* From 0 to 2 hours of the admission 
* From 2 to 4 hours of the admission
* From 4 to 6 hours of the admission
* From 6 to 12 hours of the admission 
* Above 12 hours from admission

The features can be divided into four different categories:

* Patient demographic information(3)
* Patient previous grouped diseases(9)
* Blood results (36)
* Vital signs(6)

Some notes:

* For each factor in the blood results mean, median, max, min, diff have been provided which leads to 36 * 5 = 180 features.
* For each factor vital sign mean, median, max, min, diff and relative diff have been provided which leads to 6 * 6 = 36 features.
* Total number of features is 228.

### Missing data ###
There are some missing values in the dataset.
The dataset provider mentioned that it is better to fill missing values with respect to previous or next entry of the same patient. When patient has stable situation they do not measure all the features so neighbor time window can be used.

So we used previous time window of each patient to fill the patient's missing values

### The earlier, the better! ###
The dataset provider mentioned that it is better to create the predictive model using the first time window instead of using all time windows.

We removed all the records with ICU=1 since we want to predict addmission before it has happend.

all the records of patinet with ICU=0 are considered as admited label if the patient has at least one record with ICU=1
all the records of patinet with ICU=0 are considered as not admited label if the patient has no record with ICU=1

### How to run
`python run.py`