"""
    Sentiment Analysis Add-on
"""

import csv
import re

from documentcloud.addon import AddOn
from happytransformer import HappyTextClassification
import nltk

# download the sentence parser from NLTK. 
# gives the ability to break a bunch of text down into sentences.
nltk.download("punkt")

# also get the distilbert text classifier from HuggingFace's HappyTransformer.
tc = HappyTextClassification(model_type="DISTILBERT", model_name="distilbert-base-uncased-finetuned-sst-2-english", num_labels=2) 

class Sentiment(AddOn):

    def main(self):

        # provide at least one document.
        if not self.documents:
            self.set_message("Please select at least one document")
            return

        with open("sentiment.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(["document_title", "sentence", "sentiment_label", "sentiment_valence"])

            for document in self.client.documents.list(id__in=self.documents):

                # break document text into sentences
                sentences = nltk.tokenize.sent_tokenize(document.full_text)

                # for each sentence, write the document's title, which sentence in the document
                # we've analyzed, and what the sentiment breakdown is.
                for sentence in sentences:
                    sentiment_object = tc.classify_text(sentence)
                    writer.writerow(
                        [document.title, [sentence], sentiment_object.label, sentiment_object.score] 
                    )

            self.upload_file(file_)


if __name__ == "__main__":
    Sentiment().main()
