"""
GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv
import math
import os

from openai import OpenAI
from documentcloud.addon import AddOn
import tiktoken 

client = OpenAI(api_key=os.environ["TOKEN"])

encoding = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

AVERAGE_CHARS_PER_PAGE = 1500
MAX_PAGES = 40

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
            total_num_pages = 0
            for document in self.get_documents():
                full_text = document.full_text
                num_characters = len(full_text)
                num_pages = ceil(num_characters / AVERAGE_CHARS_PER_PAGE)
                num_pages = max(1,num_pages) # In case there is a 1 page document with no text, we don't error out. 
                num_pages = min(num_pages, MAX_PAGES)
                total_num_pages += num_pages
            ai_credit_cost = total_num_pages 
            try:
                self.charge_credits(ai_credit_cost)
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
                        :56000
                    ]  # Limiting to first 56k characters from entire document
                    submission = (
                        f"Assignment:\n=============\n{user_input}\n\n"
                        f"Document Text:\n=========\n{full_text}\n\n\n"
                        "Answer:\n==========\n"
                    )
                    message=[
                        {"role": "Document Reader", "content": submission}
                    ]
                    response = client.chat.completions.create(messages=message, model=gpt_model, temperature=0.2, max_tokens=1000, top_p=1, frequency_penalty=0, presence_penalty=0)
                    result = response.choices[0].message.content
                
                    writer.writerow([document.title, document.canonical_url, result])
                    if self.data.get("value"):
                        try:  # should add a proper permission check here.
                            document.data[self.data["value"]] = [str(result)]
                            document.save()
                        except:
                            print("Saving the value did not work")
                except Exception as e:
                    print(f"Error: {e}")

            self.upload_file(file_)


if __name__ == "__main__":
    GPTPlay().main()
