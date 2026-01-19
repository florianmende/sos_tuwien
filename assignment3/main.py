from scipy.io import arff
import pandas as pd
import numpy as np
import os
from som_toolbox import somtoolbox
from som_toolbox.SOMToolBox_Parse import SOMToolBox_Parse
from som_toolbox.somtoolbox import SOMToolbox
from minisom import MiniSom
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

def main():

    # Load the dataset
    data_path = os.path.join("data")
    data = arff.loadarff(os.path.join(data_path, "credit-g.arff"))

    # Convert the dataset to a pandas DataFrame
    df = pd.DataFrame(data[0])

    # Decode byte strings in object columns
    for col in df.select_dtypes([object]).columns:
        df[col] = df[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
    
    # Encode categorical variables to numeric
    df_encoded = df.copy()
    label_encoders = {}
    for col in df_encoded.select_dtypes([object]).columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        label_encoders[col] = le
    
    # Convert to numpy array for minisom
    data_array = df_encoded.values.astype(float)
    
    # Scale the data to [0, 1] range
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data_array)
        
    SOM_X_AXIS_NODES  = 8
    SOM_Y_AXIS_NODES  = 8
    SOM_N_VARIABLES  = data_scaled.shape[1]
    som = MiniSom(SOM_X_AXIS_NODES, SOM_Y_AXIS_NODES, SOM_N_VARIABLES)
    ALPHA = 0.5
    DECAY_FUNC = 'linear_decay_to_zero'
    SIGMA0 = 1.5
    SIGMA_DECAY_FUNC = 'linear_decay_to_one'
    NEIGHBORHOOD_FUNC = 'triangle'

    som.pca_weights_init(data_scaled)
    N_ITERATIONS = 5000
    som.train_random(data_scaled, N_ITERATIONS, verbose=True)  
    
    # Reshape weights from (m, n, dimension) to (m*n, dimension) for SOMToolbox
    weights_3d = som.get_weights()  # Shape: (m, n, dimension)
    weights_2d = weights_3d.reshape(SOM_X_AXIS_NODES * SOM_Y_AXIS_NODES, SOM_N_VARIABLES)  # Shape: (m*n, dimension)
    
    # Convert classes to numpy array
    classes_array = df_encoded['class'].values if 'class' in df_encoded.columns else None
    
    # Convert component_names to list (not numpy array) to avoid boolean evaluation issues
    component_names_list = df_encoded.columns.tolist()
    
    sm = SOMToolbox(weights=weights_2d, m=SOM_X_AXIS_NODES, n=SOM_Y_AXIS_NODES,
                dimension=SOM_N_VARIABLES, input_data=data_scaled,
               classes=classes_array, component_names=component_names_list)
    sm._mainview


if __name__ == "__main__":
    main()
