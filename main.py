"""
    TheFuzz Implementation as a DocumentCloud Add-on
    https://github.com/seatgeek/thefuzz
"""

import csv
import re

from documentcloud.addon import AddOn
from thefuzz import fuzz
from thefuzz import process


class TheFuzz(AddOn):
    def main(self):

        # provide at least one document.
        if not self.documents:
            self.set_message("Please select at least one document")
            return

        with open("compared_docs.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(
                ["document_title", "url", "similarity"]
            )
            
            reference_doc = self.client.documents.get(self.data.get("reference_doc"))

            for document in self.client.documents.list(id__in=self.documents):
                score =  str(fuzz.ratio(reference_doc.full_text, document.full_text))
                writer.writerow(
                    [
                        document.title,
                        document.canonical_url,
                        str(score)
                    ]
                )
#                self.set_message(str("The document [", document.title, "]/(", document.canonical_url, "scored ", score))
            self.upload_file(file_)


if __name__ == "__main__":
    TheFuzz().main()
