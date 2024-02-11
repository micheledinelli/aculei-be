import pandas as pd

# Load the dataframe
df = pd.read_pickle('app/db/static/aculei.pkl')

# View for selecta
selecta_df = pd.read_pickle('app/db/static/aculei_selecta.pkl')

# View for insights
camera_df = pd.read_pickle('app/db/static/camera.pkl')