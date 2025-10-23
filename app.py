# 以下を「app.py」に書き込み
import streamlit as st
import spacy
from spacy.pipeline import EntityRuler
from spacy import displacy
import json
import base64

# GiNZAモデルの読み込み
nlp = spacy.load("ja_ginza")

# EntityRulerの作成
ruler = nlp.add_pipe("entity_ruler", before="ner")

# 読み込むJSONファイル名のリスト
pattern_files = [
    "ginza_patterns_clinic_matsumoto-oomachi-kiso.json",
    "ginza_patterns_clinic_matsumoto-shi.json",
    "ginza_patterns_hospital.json",
    "ginza_patterns_houkan.json",
    "patterns_trinity_facility.json",
    "patterns_trinity_name.json"
]

# 各ファイルからパターンを読み込む
for file in pattern_files:
    with open(file, encoding="utf-8") as f:
        patterns = json.load(f)
        ruler.add_patterns(patterns)

# テキストを適切な長さに分割
def split_text(text, max_length=4000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Streamlit アプリの設定
st.title("カスタムGiNZAでNERマスキング2")
text_input = st.text_area("テキストを入力してください", height=300)

if st.button("解析開始"):
    text = text_input
    chunks = split_text(text)

    # エンティティのラベル定義
    location_labels = [
        "Country", "City", "GPE_Other", "Occasion_Other", "Location",
        "Location_Other", "Domestic_Region", "Province", "Station",
        "Continental_Region", "Theater","Mountain","Island"
    ]

    facility_labels = [
        "Facility", "Organization", "Company", "School", "Facility_Other",
        "International_organization", "GOE_Other", "Show_organization","Organization_Other",
        "Corporation_Other","Trinity_ryakusho","Byoin","Hokan","Shinryojo","Spa","N_Organization","Food_Other","Public_Institution"
    ]

    person_labels = [
        "Person","Trinity_name"
    ]

    # 分割されたテキストを解析し、エンティティ情報を保存
    all_entities = []
    modified_text_parts = []

    for chunk in chunks:
        doc = nlp(chunk)
        chunk_modified_text = chunk

        sorted_ents = sorted(doc.ents, key=lambda x: len(x.text), reverse=True)

        for ent in sorted_ents:
            all_entities.append((ent.text, ent.label_))
            if ent.label_ in location_labels:
                chunk_modified_text = chunk_modified_text.replace(ent.text, "[Location]")
            elif ent.label_ in facility_labels:
                chunk_modified_text = chunk_modified_text.replace(ent.text, "[Facility]")
            elif ent.label_ in person_labels:
                chunk_modified_text = chunk_modified_text.replace(ent.text, "[Person]")

        modified_text_parts.append(chunk_modified_text)

    modified_text = ''.join(modified_text_parts)

    st.subheader("変換後のテキスト")
    st.text_area("変換後のテキスト", value=modified_text, height=300)

    st.subheader("エンティティ")
    for entity in all_entities:
        st.write(f"Entity: {entity[0]}, Label: {entity[1]}")

    # エンティティを可視化して表示
    for chunk in chunks:
        doc = nlp(chunk)
        filtered_ents = []
        for ent in doc.ents:
            if ent.label_ in location_labels or ent.label_ in facility_labels or ent.label_ in person_labels:
                filtered_ents.append(ent)
        doc.ents = filtered_ents
        html = displacy.render(doc, style="ent", jupyter=False)
        st.write(html, unsafe_allow_html=True)
