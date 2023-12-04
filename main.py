"""
GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv
import math
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["TOKEN"])
from documentcloud.addon import AddOn
CREDITS_PER_DOCUMENT = 14
DEFAULT_WORDS_PER_PAGE = 300

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
    def validate(self):
        """Validate that we can run the analysis"""

        if self.get_document_count() is None:
            self.set_message(
                "It looks like no documents were selected. Search for some or "
                "select them and run again."
            )
            return False
        elif not self.org_id:
            self.set_message("No organization to charge.")
            return False
        else:
            ai_credits = self.get_document_count() * CREDITS_PER_DOCUMENT
            try:
                self.charge_credits(ai_credits)
            except ValueError:
                return False
        return True

    def main(self):

        if not self.validate():
            # if not validated, return immediately
            return

        with open("compared_docs.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(["document_title", "url", "output"])
            user_input = self.data["prompt"].translate(ESCAPE_TABLE)
            gpt_model = "gpt-3.5-turbo-1106"
            for document in self.get_documents():
                self.set_message(f"Analyzing document {document.title}.")
                try:
                    # Just starting with page one for now due to API limits.
                    full_text = document.full_text.translate(ESCAPE_TABLE)[
                        :8000
                    ]  # Limiting to first 8000 characters from entire document
                    submission = (
                        f"Assignment:\n=============\n{user_input}\n\n"
                        f"Document Text:\n=========\n{full_text}\n\n\n"
                        "Answer:\n==========\n"
                    )
                    message=[
                        {"role": "user", "content": submission}
                    ]
                    response = client.chat.completions.create(messages=message, model=gpt_model, temperature=0.7, max_tokens=1000, top_p=1, frequency_penalty=0, presence_penalty=0)
                    results = response.choices[0].message['content']
                    
                    writer.writerow([document.title, document.canonical_url, results])
                    if self.data.get("value"):
                        try:  # should add a proper permission check here.
                            document.data[self.data["value"]] = [str(results)]
                            document.save()
                        except:
                            print("Saving the value did not work")
                except Exception as e:
                    print(f"Error: {e}")

            self.upload_file(file_)


if __name__ == "__main__":
    GPTPlay().main()
