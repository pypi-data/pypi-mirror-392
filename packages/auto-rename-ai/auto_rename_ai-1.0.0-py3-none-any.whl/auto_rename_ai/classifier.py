
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import EfficientNetB0, preprocess_input, decode_predictions


def load_model():
    model = EfficientNetB0(weights='imagenet')
    return model


def classify_image(img_path, model):
    """
    Loads an image from the path and preprocesses it for EfficientNetB0,
    and returns the top 1 predicted label.
    """
    # load image and resize it to 224x224(the needed size of EfficientNetB0)
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array)
    predictions = decode_predictions(preds, top=1)[0][0]# top(1)
    label = predictions[1]
    confidence = float(predictions[2])  # probability
    return label, confidence
