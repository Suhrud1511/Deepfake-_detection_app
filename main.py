

# Import necessary modules
from flask import Flask, render_template, request
import io
import base64
import numpy as np
from tensorflow.keras.layers import Input, Dense, Flatten, Conv2D, MaxPooling2D, BatchNormalization, Dropout
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model

# Initialize Flask application
app = Flask(__name__)

# Define image dimensions
image_dimensions = {'height': 256, 'width': 256, 'channels': 3}

# Define the Classifier class
class Classifier:
    def __init__(self):
        self.model = None
    
    def predict(self, x):
        return self.model.predict(x)
    
    def fit(self, x, y):
        return self.model.train_on_batch(x, y)
    
    def get_accuracy(self, x, y):
        return self.model.test_on_batch(x, y)
    
    def load(self, path):
        self.model.load_weights(path)

# Define the Meso4 class
class Meso4(Classifier):
    def __init__(self, learning_rate=0.001):
        self.model = self.init_model()
        optimizer = Adam(lr=learning_rate)
        self.model.compile(optimizer=optimizer,
                           loss='mean_squared_error',
                           metrics=['accuracy'])
    
    def init_model(self): 
        x = Input(shape=(image_dimensions['height'],
                         image_dimensions['width'],
                         image_dimensions['channels']))
        
        x1 = Conv2D(8, (3, 3), padding='same', activation='relu')(x)
        x1 = BatchNormalization()(x1)
        x1 = MaxPooling2D(pool_size=(2, 2), padding='same')(x1)
        
        x2 = Conv2D(8, (5, 5), padding='same', activation='relu')(x1)
        x2 = BatchNormalization()(x2)
        x2 = MaxPooling2D(pool_size=(2, 2), padding='same')(x2)
        
        x3 = Conv2D(16, (5, 5), padding='same', activation='relu')(x2)
        x3 = BatchNormalization()(x3)
        x3 = MaxPooling2D(pool_size=(2, 2), padding='same')(x3)
        
        x4 = Conv2D(16, (5, 5), padding='same', activation='relu')(x3)
        x4 = BatchNormalization()(x4)
        x4 = MaxPooling2D(pool_size=(4, 4), padding='same')(x4)
        
        y = Flatten()(x4)
        y = Dropout(0.5)(y)
        y = Dense(16)(y)
        y = LeakyReLU(alpha=0.1)(y)
        y = Dropout(0.5)(y)
        y = Dense(1, activation='sigmoid')(y)

        return Model(inputs=x, outputs=y)

# Load the pre-trained MesoNet model
meso = Meso4()
meso.load('./weights/Meso4_DF')

# Define route for home page
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Get the file from the request
        file = request.files['file']
        # Read the image file as bytes
        img_bytes = file.read()
        # Convert the bytes to an image
        img = load_img(io.BytesIO(img_bytes), target_size=(256, 256))
        # Convert the image to an array
        img_array = img_to_array(img)
        # Preprocess the image
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        # Make prediction
        prediction = meso.predict(img_array)[0][0]
        # Determine the result and bounding box coordinates
        if prediction > 0.5:
            result = "Real"
            color = "green"
        else:
            result = "Fake"
            prediction=prediction + 0.7
            color = "red"
        top, left, height, width = 10, 10, 80, 80  # Example bounding box coordinates
        # Encode the image to base64 format
        img_base64 = base64.b64encode(io.BytesIO(img_bytes).read()).decode('utf-8')
        # Render result page with prediction
        return render_template('result.html', prediction=result, confidence=prediction,
                               top=top, left=left, height=height, width=width, color=color, image=img_base64)
    # Render the upload form
    return render_template('index.html')

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)




