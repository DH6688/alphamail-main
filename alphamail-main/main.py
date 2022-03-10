import gmailapi
import helpers
import base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
import email
import numpy as np
import random
import models
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Activation, Dropout, Input
from tensorflow.keras.models import load_model, Model


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
m = 3000


def main():
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels and reads emails.

    Steps in program:
    1. Establish connection with Google Cloud Platform
    and Google Account.
    2. Retrieves all email IDs from account
    3. Reads all emails from IDs and stores in array
    4. Saves array of email or loads data if already stored
    5. Creates dataset from emails
    6. Trains model based on dataset
    """
    service = gmailapi.connect_gmail()
    return service


    """
    This section is for retrieving the data and generating the dataset from scratch. 
    """

    # # Get IDs of all emails
    # ids = helpers.get_ids(service, 'me', labels=[])
    # # # ids = ['17e59894494dcd05']  # ['17e512c14a0edf96'] ['17e5447f6177be15']
    #
    # # Retrieve all emails based on IDs
    # emails = helpers.read_all_emails(ids, service)
    #
    # # Save emails into file
    # helpers.save_emails(emails)
    #
    # # Generate dataset from emails
    # dataset = helpers.generate_dataset()
    #
    # # Save dataset
    # helpers.save_dataset(dataset)

    """
    This section is for loading the dataset and training the model
    """

    # dataset = helpers.load_dataset()
    #
    # training_X, training_Y = helpers.create_training_set(dataset, 0, m)
    # n = len(training_X[0])
    #
    # if os.path.isfile('model'):
    #     model = load_model('model')
    # else:
    #     model = models.model1(n)
    #     model.compile(optimizer='adam', loss='mse')
    #     model.fit(training_X, training_Y, batch_size=32, epochs=8)
    #     model.save('model', save_format='h5')
    #
    #     test_X, test_Y = helpers.create_training_set(dataset, m, m+1000)
    #     print(model.evaluate(test_X, test_Y, verbose=0))
    #
    # emails = helpers.load_emails()
    #
    # manual_test_X, manual_test_Y = helpers.create_training_set(dataset, m+1000, m+1100)
    # for i, example in enumerate(manual_test_X):
    #     print(emails[m+1000+i][2]['subject'], end='')
    #     print(model.predict(example.reshape(1, example.shape[0])))  # reshaped from (n,) to (1,n)


if __name__ == '__main__':
    main()

