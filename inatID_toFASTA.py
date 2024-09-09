import pandas as pd
from pyinaturalist import *
import pprint
import requests
import time

# list of provisional names, and list of normal names.
# pull inat observations with 

file = "C:/Users/mrozanoff/Downloads/FASTA Generator - names list.csv"

df = pd.read_csv(file)

prov_names = df['prov_names'].dropna().values.tolist()
normal_names_list = df['names'].dropna().values.tolist()



def get_observation_ids_by_field_name(provisional_name):
    # iNaturalist API endpoint for observations
    url = "https://api.inaturalist.org/v1/observations"
    
    # Parameters for the API request
    params = {
        # "q": provisional_name,
        "field:Provisional Species Name": provisional_name,
        "per_page": 200  # You can adjust this to get more results per request
    }

    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the observation IDs
        observation_ids = [obs["id"] for obs in data["results"]]
        return observation_ids
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

def get_observation_ids_by_taxon_name(taxon_name):
    # iNaturalist API endpoint for observations
    url = "https://api.inaturalist.org/v1/observations"
    
    # Parameters for the API request
    params = {
        "taxon_name": taxon_name,
        "per_page": 200  # Adjust to get more results per request if needed
    }

    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the observation IDs
        observation_ids = [obs["id"] for obs in data["results"]]
        return observation_ids
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []


genus = "Russula"


rows = []

for name in prov_names:
	search_name = genus + " " + name
	observation_ids = get_observation_ids_by_field_name(search_name)
	for obs_id in observation_ids:
		rows.append({"name": search_name, "inat_id": obs_id})

# Fetch observation IDs for normal species names using taxon name
for name in normal_names_list:
	search_name = genus + " " + name
	observation_ids = get_observation_ids_by_taxon_name(search_name)
	# Add each ID as a new row in the list
	for obs_id in observation_ids:
		rows.append({"name": search_name, "inat_id": obs_id})


df = pd.DataFrame(rows)

df = df.drop_duplicates(subset='inat_id')

print(df)

id_list = df['inat_id'].values.tolist()

clean_df = df[['name', 'inat_id']]

for id_ in id_list:
	while True:
		try:
			time.sleep(0.25)
			obs = get_observations(id=id_)

			observational_fields = obs["results"][0]["ofvs"]

			DNA = ""

			for field in observational_fields:
				if field["name"] == 'DNA Barcode ITS':
					DNA = field["value"]
					break

			clean_df.loc[clean_df.inat_id == id_, 'DNA'] = DNA
		except:
			print('hit except')
			time.sleep(30)
			continue
		break

clean_df = clean_df.dropna()
clean_df = clean_df.loc[clean_df["DNA"] != '',:]

# Writing to a FASTA file
with open('out.fasta', 'w') as f:
    for index, row in clean_df.iterrows():
        name = row['name']
        inat_id = row['inat_id']
        DNA = row['DNA']
        f.write(f'>{inat_id} {name}\n{DNA}\n')