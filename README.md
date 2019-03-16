# THE PROBLEM:
Cervical cancer is a deadly but highly treatable disease as long as
it’s detected in early stages and the correct treatment is
administered. In India, in spite of alarmingly high figures, there is
no nationwide government-sponsored screening program for
aiding women for the same.
We intend to create a system that can aid doctors in classifying
stage of cervical cancer and in turn help women in rural India get
the cervical cancer screening that could potentially save their lives
and also create awareness regarding menstrual health.
# SOLUTION APPROACH
## 1. Cervical cancer detection
### Logistic Regression Model
We started with a Logistic Regression model as a multi class classification. We spilt a small dataset for train and test data. 
We further trained a CNN model as image data is suited for. 
### CNN Model
#### Preprocessing
The initial images were large as well as irregularly shaped. We assumed that the cervix will be at the center of the image since it is the most important. 
We resized the image using opencv to set the region of interest.
A deep learning model for classifying images using a convolutional neural network with the help of batch normalisation and multi-class
logarithmic loss as our loss function. We will be working on the dataset for image-based Cervical Intraepithelial Neoplasia(CIN)
classification built from medical data archive collected by National Cancer Institute(NCI).

## 2. Geo Plotting of adversely affected areas
The results obtained from the CNN model were appended to the dataset containing geographical location of the areas.
We used bokeh library to plot on the area map and the density of points show the adversely affected areas.
