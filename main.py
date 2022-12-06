"""
GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv
import os
import re
import time

import openai
from documentcloud.addon import AddOn

openai.api_key = os.environ["TOKEN"]

ESCAPE_TABLE = str.maketrans(
    {
        "-": r"\-",
        "]": r"\]",
        "\\": r"\\",
        "^": r"\^",
        "$": r"\$",
        "*": r"\*",
        ".": r"\.",
    }
)


class GPTPlay(AddOn):
    def main(self):

        if self.get_document_count() == 0:
            self.set_message(
                "It looks like no documents were selected. Search for some or "
                "select them and run again."
            )
            return

        with open("compared_docs.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(["document_title", "url", "output"])
            user_input = self.data["prompt"].translate(ESCAPE_TABLE)
            gpt_model = self.data.get("model", "text-davinci-003"
            for document in self.get_documents():
                self.set_message(f"Analyzing document {document.title}.")
                try:
                    # Just starting with page one for now due to API limits.
                    full_text = document.get_page_text(1).translate(ESCAPE_TABLE)
                    submission = (
                        f"Assignment:\n=============\n{user_input}\n\n"
                        f"Document Text:\n=========\n{full_text}\n\n\n"
                        "Answer:\n==========\n"
                        )
                    response = openai.Completion.create(
                        model=gpt_model,
                        prompt=submission,
                        temperature=0.7,
                        max_tokens=1000,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                    )
                    results = response.choices[0].text
                    writer.writerow([document.title, document.canonical_url, results])
                    if self.data.get("value"):
                        try:  # should add a proper permission check here.
                            document.data[self.data["value"]] = [str(results)]
                            document.save()
                        except:
                            print("Saving the value did not work")
                except:
                    print("Error, moving on to the next item.")

            self.upload_file(file_)


if __name__ == "__main__":
    GPTPlay().main()
