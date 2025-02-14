MarineMonitor-ASTRA is an extension of AquaSent-TMMAE, a self-supervised learning framework developed collectively by my research institution to analyze water quality using spatiotemporal satellite imagery. While AquaSent-TMMAE introduced a robust masked autoencoder architecture for extracting water quality features, my work with MarineMonitor-ASTRA builds upon this foundation by systematically investigating the effects of different timesteps and mask ratios on model performance. Through an extensive ablation study, I optimized these parameters to enhance the accuracy of contaminant detection. This extension refines the original framework, contributing to ongoing research efforts in remote sensing and environmental monitoring.

The link to the original paper is below:
https://deepspatial2024.github.io/papers/AquaSent-TMMAE.pdf


SatMAE code from https://github.com/sustainlab-group/SatMAE (Cong et al.) and modified to incorporate Siamese framework 

Yezhen Cong, Samar Khanna, Chenlin Meng, Patrick Liu, Erik Rozi, Yutong He, Marshall Burke, David B. Lobell, and Stefano Ermon. SatMAE: Pre-training transformers for temporal and multi-spectral satellite imagery, 2023.

download_data.py - my code for downloading Sentinel-2 satellite images from Google Earth Engine for pretraining after passing in coordinates of water bodies (data csv not included due to its large size). 

After running download_data, I placed the images into three separate folders 

create_csv.py - creating a csv with paths to the images I downloaded, to be passed into main_pretrain.py. For each location, I randomly picked two images to use in pretraining. 
