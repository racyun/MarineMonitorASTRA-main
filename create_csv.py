import os
import random
import pandas as pd

# folders are called 1, 2, 3

names1 = []
names2 = []

images_a = os.listdir('satellite_data/1')
images_b = os.listdir('satellite_data/2')
images_c = os.listdir('satellite_data/3')

n = random.randint(0, 1)

for i in range(len(images_a)):
    if n > 0.5:
        # use a and b
        names1.append('satellite_data/1/' + images_a[i])
        names2.append('satellite_data/2/' + images_b[i])
    else:
        names1.append('satellite_data/2/' + images_b[i])
        names2.append('satellite_data/3/' +images_c[i])

df1 = pd.DataFrame(names1, columns=['image_path'])
df2 = pd.DataFrame(names2, columns=['image_path'])

df1.to_csv('images.csv')
df2.to_csv('images2.csv')




