def extract_fed_sentiment(speech_text):
    # Hawkish vs dovish keywords
    hawkish_words = ['inflation', 'overheating', 'tighten', 'restrictive']
    dovish_words = ['employment', 'support', 'accommodate', 'gradual']

    hawkish_matches = [word for word in hawkish_words if word in speech_text.lower()]
    dovish_matches = [word for word in dovish_words if word in speech_text.lower()]
    
    hawkish_score = sum([speech_text.lower().count(word) for word in hawkish_words])
    dovish_score = sum([speech_text.lower().count(word) for word in dovish_words])
    print(f"Hawkish words found: {hawkish_matches}")
    print(f"Dovish words found: {dovish_matches}")

    constant_rates_words = ['constant interest rate', 'interest rate unchanged']
    if constant_rates_words in speech_text:
        return 0
    
    return (hawkish_score - dovish_score) / len(speech_text.split())



file_path = '../../Fed_speeches/91725_Powell.txt'  # Replace with the actual path to your .txt file

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import nltk
from nltk.tokenize import PunktTokenizer

sent_detector = PunktTokenizer()


from transformers import BertTokenizer, BertForSequenceClassification

finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)

def finbert_sentiment_by_sentence(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    sents = sent_detector.tokenize(content.strip())
    return nlp(sents)


def aggregate_finbert_sentiment(file_path):
    score_map = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finbert_results = finbert_sentiment_by_sentence(file_path)  
    weighted_scores = []
    for result in finbert_results:
        label_score = score_map[result['label']]
        confidence = result['score']
        weighted_scores.append(label_score * confidence)
    
    return sum(weighted_scores) / len(weighted_scores)

# aggregation_91725 = aggregate_finbert_sentiment(file_path)
# print(aggregation_91725)

# aggregation_32024 = aggregate_finbert_sentiment('../../Fed_speeches/32024_Powell.txt')
# print(aggregation_32024)