"""
This is an add-on to search a document for a regex and output all of the matches
"""

import csv
import re

from documentcloud.addon import AddOn


class Regex(AddOn):
    def main(self):
        if not self.documents:
            self.set_message("Please select at least one document")
            return

        regex = self.data["regex"]
        pattern = re.compile(regex)

        with open("matches.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(["match", "url"])

            for document in self.client.documents.list(id__in=self.documents):
                writer.writerows(
                    [m, document.canonical_url]
                    for m in pattern.findall(document.full_text)
                )

            self.upload_file(file_)


if __name__ == "__main__":
    Regex().main()
