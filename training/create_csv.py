import os
import json
import pandas as pd
from transformers import T5Tokenizer


image_path = "../dataset/images"
json_path = "../dataset/json" 

image_path_list = os.listdir(image_path)
json_path_list = os.listdir(json_path)

tokenizer = T5Tokenizer.from_pretrained("t5-small")

temp = pd.DataFrame(columns=["image_path", "items", 'tokenized_items'])

for i, j in zip(image_path_list, json_path_list):
    items = ""
    json_data = json.load(open(os.path.join(json_path, j), 'r'))

    for k in json_data["items"]:
        items += k["name"] + ","

    ## Replace the last comma with a period
    items = items[:-1] + "."
    
    tokenized_items = tokenizer(items, padding="max_length", truncation=True, max_length=512, return_tensors="pt")["input_ids"][0].tolist()
    image = os.path.join(image_path, i)

    temp = pd.concat([temp, pd.DataFrame({"image_path": [image], "items": [items], 'tokenized_items': [tokenized_items]})], ignore_index=True)

temp.to_csv("../dataset/dataset.csv", index=False)
