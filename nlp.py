import joblib
import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Load model Naive Bayes (akurasi 75%) dan vectorizer
model = joblib.load('model_final.pkl')
tfidf = joblib.load('tfidf_vectorizer.pkl')

# Setup preprocessing
stop_factory = StopWordRemoverFactory()
stopword_remover = stop_factory.create_stop_word_remover()
stem_factory = StemmerFactory()
stemmer = stem_factory.create_stemmer()

def preprocess_text(text):
    text = str(text).lower()
    text = text.encode('ascii', 'ignore').decode('ascii')  # hapus emoji
    text = re.sub(r'[^a-z\s]', '', text)                   # hanya huruf kecil
    text = re.sub(r'\s+', ' ', text).strip()
    text = stopword_remover.remove(text)
    text = stemmer.stem(text)
    return text

def detect_priority(text):
    text_bersih = preprocess_text(text)
    text_tfidf  = tfidf.transform([text_bersih])
    hasil       = model.predict(text_tfidf)[0]
    return hasil