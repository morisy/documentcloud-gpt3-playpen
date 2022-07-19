"""
    TheFuzz Implementation as a DocumentCloud Add-on
    https://github.com/seatgeek/thefuzz
"""

import csv
import re
import time

from documentcloud.addon import AddOn
from thefuzz import fuzz
from thefuzz import process


class TheFuzz(AddOn):
    def main(self):
        documents = []
        # provide at least one document.
        if self.documents:
            self.set_message("Running analysis on selected documents.")
            for document in self.documents:
                self.set_message(f"Adding {document} to the analysis queue.")
                documents.append(str(document))
        else:
            self.set_message("Running analysis on search results.")
            for document in self.client.documents.search(self.query):
                self.set_message(f"Adding {document.id} to the analysis queue.")
                documents.append(str(document))
        
        self.set_message(f"The documents to be analyzed are {str(documents)}.")
        time.sleep(5.5)
                
        with open("compared_docs.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(
                ["document_title", "url", "similarity"]
            )
            
            reference_doc = self.client.documents.get(self.data.get("reference_doc"))
            self.set_message(f"Working on analyzing {str(len(self.documents))} documents.")
            for doc_id in documents:
                document = self.client.documents.get(doc_id)
                score =  str(fuzz.ratio(reference_doc.full_text, document.full_text))
                self.set_message(f"The document {document.title} scored {score}.")
                writer.writerow(
                    [
                        document.title,
                        document.canonical_url,
                        str(score)
                    ]
                )
            self.upload_file(file_)


if __name__ == "__main__":
    TheFuzz().main()
