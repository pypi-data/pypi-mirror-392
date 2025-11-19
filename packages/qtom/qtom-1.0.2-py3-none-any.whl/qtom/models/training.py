import numpy as np
import keras
from keras.callbacks import ModelCheckpoint, EarlyStopping
from .neural_network import build_model

def train_model(dim, data_file, model_save_path, epochs = 2000):
    """Train the model on saved data."""
    print(f"Loading data from {data_file}...")
    data = np.load(data_file)
    X_train = data['train_input']
    y_train = data['train_output']
    X_val = data['val_input']
    y_val = data['val_output']

    print(f"Training data: {X_train.shape}, Output: {y_train.shape}")

    input_dim = dim**2
    output_dim = dim**2

    print(f"Building model with input_dim={input_dim}, output_dim={output_dim}")
    model = build_model(input_dim, output_dim)

    checkpoint = ModelCheckpoint(
        model_save_path,
        monitor='val_mean_squared_error',
        save_best_only=True,
        mode='min',
        verbose=1
    )
    
    early_stop = EarlyStopping(
        monitor='val_mean_squared_error',
        mode='min',
        patience=200,
        verbose=1
    )
    
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        batch_size=100,
        epochs=epochs,
        validation_data=(X_val, y_val),
        callbacks=[checkpoint, early_stop],
        verbose=2
    )
    
    return model, history
