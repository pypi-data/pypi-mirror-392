import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Nadam

def build_model(input_dim, output_dim, seed=42):
    """Build the neural network architecture for quantum tomography."""
    model = Sequential()

    model.add(Dense(200, input_shape=(input_dim,), activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(180, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(180, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(160, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(160, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(160, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(160, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(100, activation='relu',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))
    model.add(Dense(output_dim, activation='tanh',
                   kernel_initializer=keras.initializers.glorot_normal(seed=seed)))

    model.compile(loss='mse', optimizer=Nadam(), metrics=['mean_squared_error'])
    return model
