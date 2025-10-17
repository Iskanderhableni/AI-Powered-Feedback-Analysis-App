import langdetect as ld
from transformers import MarianMTModel, MarianTokenizer 
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from accelerate import Accelerator
import os
import pandas as pd
os.environ["HF_HOME"] = "D:/huggingface_cache"
import brainAI as ba
import csv





def language_dect(input_text):
    detected_lang = ld.detect_langs(input_text)
    print(detected_lang)
    lang = detected_lang[0].lang
    conf = detected_lang[0].prob
    print(f"Detected: {lang}, Confidence: {conf}")

    return lang, conf



def translate_text_to_english(input_text, source_lang):
        cache_dir="D:/huggingface_cache"

        model_name = "Helsinki-NLP/opus-mt-mul-en"
        accelerator = Accelerator()

        if source_lang == 'en':
            return input_text
        else:
            tokenizer = MarianTokenizer.from_pretrained(model_name,cache_dir=cache_dir)
            model = MarianMTModel.from_pretrained(model_name,cache_dir=cache_dir)
            tokenizer,model = accelerator.prepare(tokenizer, model)
            input = tokenizer(input_text, return_tensors="pt", padding=True)
            translated = model.generate(**input)

            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            print(f"Translated Text: {translated_text}")
            return translated_text


def cleaned_review(input_review):
      cache_dir="D:/huggingface_cache"
      accelerator = Accelerator()
      parssed_input = str(input_review)
      clean_model_name = "pszemraj/flan-t5-large-grammar-synthesis"
      cleaner_tokenizer = AutoTokenizer.from_pretrained(clean_model_name,cache_dir=cache_dir)
      cleaner_model = AutoModelForSeq2SeqLM.from_pretrained(clean_model_name,cache_dir=cache_dir)
      cleaner_model, cleaner_tokenizer = accelerator.prepare(cleaner_model, cleaner_tokenizer)
      input_to_clean = cleaner_tokenizer(parssed_input, return_tensors="pt", padding=True)
      cleaned_text = cleaner_tokenizer.decode(cleaner_model.generate(**input_to_clean)[0], skip_special_tokens=True)
      print(f"Cleaned Text: {cleaned_text}")
     


import pandas as pd
import csv

if __name__ == "__main__":
    review_file = pd.read_csv('../src/agoda_reviews.csv')
    agoda_clean_reviews = 'agoda_clean_reviews.csv'

    # Write header once
    with open(agoda_clean_reviews, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Clean Review', 'Rating'])

    for i, row in review_file.iterrows():
        sample_text = row['review']
        review_rating = row['rating']
        print(f"Original Review: {sample_text} | Rating: {review_rating}")

        lang, conf = language_dect(sample_text)
        if lang != 'en' and conf > 0.7:
            print(f"Translating from {lang} to English...")
            translated_review = translate_text_to_english(sample_text, lang)
            print(f"Translated Review but still not clean: {translated_review}")
            final_review_response = ba.generate_suitable_review_response(translated_review)
        elif lang == 'en' and conf > 0.7:
            final_review_response = ba.generate_suitable_review_response(sample_text)
        else:
            print("Low confidence in language detection; skipping translation.")
            continue

        print(f"Final Review Response: {final_review_response}")

        # Append to CSV
        with open(agoda_clean_reviews, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([final_review_response, review_rating])
            print(f"Appended cleaned review to {agoda_clean_reviews}")