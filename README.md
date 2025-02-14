SatMAE code from https://github.com/sustainlab-group/SatMAE (Cong et al.) and modified to incorporate Siamese framework 

Yezhen Cong, Samar Khanna, Chenlin Meng, Patrick Liu, Erik Rozi, Yutong He, Marshall Burke, David B. Lobell, and Stefano Ermon. SatMAE: Pre-training transformers for temporal and multi-spectral satellite imagery, 2023.

download_data.py - my code for downloading Sentinel-2 satellite images from Google Earth Engine for pretraining after passing in coordinates of water bodies (data csv not included due to its large size). 

After running download_data, I placed the images into three separate folders 

create_csv.py - creating a csv with paths to the images I downloaded, to be passed into main_pretrain.py. For each location, I randomly picked two images to use in pretraining. 
