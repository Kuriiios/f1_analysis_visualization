import torch
import torchaudio
from torch_audiomentations import Gain, ApplyImpulseResponse
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
from pydub import AudioSegment
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
import requests
import fastf1
import requests
from bs4 import BeautifulSoup
import json
import codecs
import pandas as pd
torch.cuda.empty_cache()
torch.manual_seed(0)

from pathlib import Path
parent_file = Path(__file__).resolve().parent.parent.parent.parent
save_folder_transcription = '/f1_analysis/data_dashboard/'
save_path = str(parent_file) + save_folder_transcription
print(save_path)

def run_inference(audio_path: str, language: str, pipe, output_path: str):
    result = pipe(audio_path, generate_kwargs={"language": language})
    with open(output_path, "w") as f:
        f.write(result["text"])
    print("Transcription complete. Saved to:", output_path)

def download(url, path):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)

def audio_to_txt(audio_url):
    download(audio_url, './speech.wav')

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch_dtype = torch.float32
    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device.type if device.type == 'cpu' else "cuda:0"
    )

    run_inference("./speech.wav", "en", pipe, "improved_audio.txt")
    os.remove("./speech.wav")
    with open('improved_audio.txt', 'r') as file:
        data = file.read().replace('\n', '')
    return data

def get_uncreated_team_radio(year, race_number):
    session= fastf1.get_session(year, race_number, 'R')
    session.load()

    path = str(year) + '/' + str(session.event['Session5Date'])[:10] + '_'+ str(session.event['EventName']).replace(' ','_') + '/' +str(session.event['Session5Date'])[:10]+'_'+str(session.event['Session5']) + '/'
    resource_name = 'https://livetiming.formula1.com/static/'
    full_url = resource_name + path + 'TeamRadio.json'

    page = requests.get(full_url)
    soup = BeautifulSoup(page.text, "html.parser")

    site_json=json.loads(soup.text[1:])
    date_list = []
    driver_number_list = []
    new_url_list = []
    transcription_list = []
    for i in range(0, len(list(site_json.values())[0])):
        val_json = list(list(site_json.values())[0][i].values())
        date_list.append(val_json[0].replace('T', ' ')[:19])
        driver_number_list.append(val_json[1])
        new_url_list.append(resource_name + path + val_json[2])
        transcription_list.append(audio_to_txt(resource_name + path + val_json[2]))
    df = pd.DataFrame({'Time' :date_list, 'transcription': transcription_list, 'url': new_url_list}, index = driver_number_list)
    os.remove("./improved_audio.txt")
    df.to_csv(str(save_path) + (str(session.event.Session5Date)[:10]+'_'+str(session.event.EventName).replace(' ','_')+'.csv'))

year = int(input('Year ? '))
race_number = int(input('Race Number ? (1-24) '))
get_uncreated_team_radio(year, race_number)