import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
import os

st.set_page_config(page_title="KaryoVision", layout="centered")
API_KEY = st.secrets["API_KEY"]

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
)

MUTATION_TYPE_MAPPING = {
    "deletion": {
        "disorders": [
            {"name": "Cri du Chat syndrome", "chromosome": 5},
            {"name": "DiGeorge syndrome", "chromosome": 22},
            {"name": "Williams syndrome", "chromosome": 7},
            {"name": "Angelman syndrome", "chromosome": 15, "type": "Maternal"},
            {"name": "Prader-Willi syndrome", "chromosome": 15, "type": "Paternal"},
            {"name": "Roberts syndrome", "chromosome": 8},
            {"name": "Turner syndrome", "chromosome": 23},
            {"name": "45,X/46,XX mosaicism", "chromosome": 23},
            {"name": "Friedreich's ataxia", "chromosome": 9},
            {"name": "Ehlers-Danlos syndrome (classic type)", "chromosome": 9},
            {"name": "Phelan-McDermid syndrome", "chromosome": 22},
            {"name": "Wolf-Hirschhorn syndrome", "chromosome": 4},
            {"name": "Alagille syndrome", "chromosome": 20}
        ]
    },
    "extra": {
        "disorders": [
            {"name": "Down syndrome (Trisomy 21)", "chromosome": 21},
            {"name": "Edwards syndrome (Trisomy 18)", "chromosome": 18},
            {"name": "Patau syndrome (Trisomy 13)", "chromosome": 13},
            {"name": "Klinefelter syndrome", "chromosome": 23},
            {"name": "Triple X syndrome", "chromosome": 23},
            {"name": "XYY syndrome", "chromosome": 23},
            {"name": "Tetrasomy 18p", "chromosome": 18},
            {"name": "Tetrasomy 9p", "chromosome": 9}
        ]
    },
    "mutation": {
        "disorders": [
            {"name": "Fragile X syndrome", "chromosome": 23},
            {"name": "Beta-Thalassemia", "chromosome": 11},
            {"name": "Alpha-Thalassemia", "chromosome": 16},
            {"name": "Huntington's disease", "chromosome": 4},
            {"name": "Cystic fibrosis", "chromosome": 7},
            {"name": "Sickle cell anemia", "chromosome": 11},
            {"name": "Marfan syndrome", "chromosome": 15},
            {"name": "Neurofibromatosis type 1", "chromosome": 17},
            {"name": "Achondroplasia", "chromosome": 4}
        ]
    },
    "other": {
        "disorders": [
            {"name": "Alder-Reilly syndrome", "chromosome": 9},
            {"name": "Familial Mediterranean fever", "chromosome": 16},
            {"name": "Ataxia-telangiectasia", "chromosome": 11},
            {"name": "Ehlers-Danlos syndrome (hypermobile type)", "chromosome": 1},
            {"name": "Bardet-Biedl syndrome", "chromosome": 11},
            {"name": "Retinitis pigmentosa", "chromosome": 6},
            {"name": "Usher syndrome", "chromosome": 11},
            {"name": "Stargardt disease", "chromosome": 1}
        ]
    }
}

def draw_bounding_boxes(image, detections):
    draw = ImageDraw.Draw(image)
    for detection in detections:
        x0 = detection['x'] - detection['width'] / 2
        y0 = detection['y'] - detection['height'] / 2
        x1 = detection['x'] + detection['width'] / 2
        y1 = detection['y'] + detection['height'] / 2
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
    return image

st.title("KaryoVision 🧬")

uploaded_file = st.file_uploader("Upload a chromosome image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    image_path = "uploaded_image.jpg"
    image.save(image_path)

    result = CLIENT.infer(image_path, model_id="chromosomes-24-types/1")

    if 'predictions' in result:
        detections = result['predictions']
    else:
        st.error("No predictions found. Please check the image and model settings.")
        detections = []

    df = pd.DataFrame(detections)
    df = df.drop(columns=['detection_id'], errors='ignore')
    grouped_df = df.groupby('class_id').size().reset_index(name='count')

    st.write("### Detection Results Grouped by Class ID")
    st.dataframe(grouped_df)

    image_with_boxes = draw_bounding_boxes(image.copy(), detections)
    st.image(image_with_boxes, caption="Detected Image with Bounding Boxes", use_column_width=True)

    disorder_results = []

    for index, row in grouped_df.iterrows():
        class_id = row['class_id']
        count = row['count']
        if count < 2:
            for disorder in MUTATION_TYPE_MAPPING["deletion"]["disorders"]:
                if disorder["chromosome"] == class_id:
                    disorder_results.append({
                        "disorder": disorder["name"],
                        "position": class_id,
                        "missing": 2 - count,
                        "mutation_type": "Deletion"
                    })
                    break
        elif count > 2:
            for disorder in MUTATION_TYPE_MAPPING["extra"]["disorders"]:
                if disorder["chromosome"] == class_id:
                    disorder_results.append({
                        "disorder": disorder["name"],
                        "position": class_id,
                        "extra": count - 2,
                        "mutation_type": "Extra"
                    })
                    break

    for index, row in grouped_df.iterrows():
        class_id = row['class_id']
        for disorder in MUTATION_TYPE_MAPPING["mutation"]["disorders"]:
            if disorder["chromosome"] == class_id:
                disorder_results.append({
                    "disorder": disorder["name"],
                    "position": class_id,
                    "mutation_type": "Mutation"
                })

    if disorder_results:
        results_df = pd.DataFrame(disorder_results)
        results_df['missing'] = results_df.get('missing', pd.Series([None]*len(results_df)))
        results_df['extra'] = results_df.get('extra', pd.Series([None]*len(results_df)))
        results_df.rename(columns={'position': 'Chromosome Position'}, inplace=True)

        st.subheader("Predicted Genetic Disorders and Mutation Types:")
        st.dataframe(results_df[['disorder', 'Chromosome Position', 'mutation_type', 'missing', 'extra']].fillna('-'))
    else:
        st.write("No genetic disorders or mutation types predicted based on the detected chromosomes.")
