import urllib.request
import json
import os

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_real_sample(folder, out_name):
    print(f"Fetching real file list from {folder}...")
    url = f"https://api.github.com/repos/gveres/donateacry-corpus/contents/donateacry_corpus_cleaned_and_updated_data/{folder}"
    
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
        # Get the first .wav file
        for item in data:
            if item['name'].endswith('.wav'):
                download_url = item['download_url']
                print(f"Downloading {item['name']}...")
                
                # Download it to the Desktop
                desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", out_name)
                
                req_dl = urllib.request.Request(download_url, headers=HEADERS)
                with urllib.request.urlopen(req_dl) as dl_res, open(desktop_path, 'wb') as f:
                    f.write(dl_res.read())
                
                print(f"Saved to {desktop_path}")
                return

if __name__ == "__main__":
    try:
        get_real_sample("hungry", "REAL_DATASET_HUNGER_CRY.wav")
        get_real_sample("belly_pain", "REAL_DATASET_DISCOMFORT_CRY.wav")
    except Exception as e:
        print(f"Error: {e}")
