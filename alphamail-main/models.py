import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Activation, Dropout, Input
from tensorflow.keras.models import load_model, Model
import tensorflow_hub as hub
import tensorflow_text


def model2():
    """
    Based on BERT model as outlined by
    https://www.analyticsvidhya.com/blog/2021/09/performing-email-spam-detection-using-bert-in-python/
    Takes in a string subject line of arbitrary length and applies encoding before returning importance score
    """
    bert_preprocessor = hub.KerasLayer('https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3')
    bert_encoder = hub.KerasLayer('https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4')
    text_input = Input(shape=(), dtype=tf.string)
    preprocessed_text = bert_preprocessor(text_input)
    encoded = bert_encoder(preprocessed_text)
    dropout = Dropout(0.1)(encoded['pooled_output'])
    output = Dense(1, activation='sigmoid')(dropout)

    model = Model(inputs=[text_input], outputs=output)

    return model


def model1(n_inputs):
    """
    Model 1 takes in the input of dictionary length and
    utilizes dense layers in order to calculate the coefficients
    associated with word frequencies in order to output
    the importance of an email.
    """
    X_input = Input(shape=n_inputs)
    X = Dense(units=64, activation='relu')(X_input)
    X = Dense(units=32, activation='relu')(X)
    X = Dropout(0.2)(X)
    output = Dense(units=1, activation='sigmoid')(X)

    model = Model(inputs=X_input, outputs=output)

    return model
