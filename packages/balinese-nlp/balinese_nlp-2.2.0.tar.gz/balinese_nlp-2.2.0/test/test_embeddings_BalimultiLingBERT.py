from balinese_nlp.embeddings.BERT import BalimultiLingBERT
from transformers import pipeline


bert = BalimultiLingBERT()
fine_tuned_model = bert.load_pretrained_model()


# print finetuned model
print(fine_tuned_model)

# Test 1 - Masked Language Modelling
# Inisialisasi pipeline fill-mask
# Pastikan Anda menggunakan model_mlm untuk tugas ini
tokenizer = fine_tuned_model['tokenizer']
model_mlm = fine_tuned_model['model_mlm']
fill_mask_pipeline = pipeline("fill-mask", model=model_mlm, tokenizer=tokenizer)

# Contoh kalimat berbahasa Bali dengan kata yang di-mask
text_mlm = "Ring Bali, krama sane dados [MASK] patut ngutsahayang idup."
print(f"Contoh kalimat: {text_mlm}")

# Prediksi kata yang paling mungkin
predictions = fill_mask_pipeline(text_mlm)

print("\nHasil Prediksi (Masked Language Modeling):")
for p in predictions:
    print(f"- '{p['token_str']}' (Skor: {p['score']:.4f})")