from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
from google import genai

model_name = "gemini-2.5-flash"

def generate_suitable_review_response(review_text):
    cache_dir = "D:/huggingface_cache"

    client = genai.Client(api_key="API-KEY")

    prompt = (
       # "Rewrite the following hotel review in clear, fluent English, "
        #"keeping all details exactly as they are:\n\n"
        #"all I need is the answer only without "
         "Rewrite the following review in very short, clear, and natural English. "
    "Keep the exact meaning and sentiment (positive, neutral, or negative). "
    "Preserve key ideas but remove extra words. "
    "Output only the improved short version, no explanations."
    "just keywords separated by comma.\n\n"

    f"Review: {review_text}"
    )

    response = client.models.generate_content(model=model_name, contents=prompt )

    #
    return response.text




def generate_suitable_review_response_rebetter(review_text):
    cache_dir = "D:/huggingface_cache"

    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)

    # Load model (T5 uses Seq2SeqLM)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        device_map="auto" if torch.cuda.is_available() else None
    )

    # Build pipeline
    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1
    )

    # Better prompt to preserve all details
    prompt = (
        "Rewrite the following hotel review in clear, fluent English, "
        "keeping all details exactly as they are just reimprove it :\n\n"
        f"{review_text}"
    )

    # Generate response
    result = pipe(
        prompt,
        max_new_tokens=400,     # longer output to include all details
        do_sample=False,        # deterministic output
        num_beams=5,            # beam search for better quality
        repetition_penalty=2.5, # discourage loops/repeats
        early_stopping=True
    )[0]['generated_text']

    return result
