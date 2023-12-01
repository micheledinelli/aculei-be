import pandas as pd
import os

df = pd.read_csv("aculei.csv")

image_directory = 'aculei-images-test'
image_names = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.jpeg')]
df_test = df[df['image_name'].isin(image_names)]
print(df_test.shape)
df_test.to_csv("aculei-test.csv")