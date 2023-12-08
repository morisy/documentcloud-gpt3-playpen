"""
GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv
import math
import os
import sys
import time

from openai import OpenAI
from documentcloud.addon import AddOn

client = OpenAI(api_key=os.environ["TOKEN"])

AVERAGE_CHARS_PER_PAGE = 1750
MAX_PAGES = 32
DEFAULT_CHAR_LIMIT = 54000

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
    def calculate_cost(self, documents, limiter=None):
        total_num_pages = 0
        for doc in documents:
            full_text = doc.full_text
            if limiter:
                full_text = full_text[:limiter]  # Use limiter if provided
            num_characters = len(full_text)
            num_pages = math.ceil(num_characters / AVERAGE_CHARS_PER_PAGE)
            num_pages = max(1, num_pages)
            num_pages = min(num_pages, MAX_PAGES)
            total_num_pages += num_pages
        cost = total_num_pages
        return cost
        
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
            character_limit = self.data.get("limiter", DEFAULT_CHAR_LIMIT)
            ai_credit_cost = self.calculate_cost(self.get_documents(), limiter=character_limit)
        try:
            self.charge_credits(ai_credit_cost)
        except ValueError:
            return False
        return True

    def dry_run(self, documents):
        character_limit = self.data.get("limiter", DEFAULT_CHAR_LIMIT)
        cost = self.calculate_cost(documents, limiter=character_limit)

        self.set_message(
            f"There are {cost} standard size pages in this document set. "
            f"It would cost {cost} AI credits to run your prompt on the set."
        )
        sys.exit(0)
        
    def main(self):
        character_limit = DEFAULT_CHAR_LIMIT
        if self.data.get("limiter"):
            character_limit = self.data.get("limiter")
        # If dry_run is selected, it will calculate the cost of translation. 
        if self.data.get("dry_run"):
            self.dry_run(self.get_documents())
            
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
                        :character_limit
                    ]  # Limiting to first 54k characters from entire document
                    submission = (
                        f"Assignment:\n=============\n{user_input}\n\n"
                        f"Document Text:\n=========\n{full_text}\n\n\n"
                        "Answer:\n==========\n"
                    )
                    message=[
                        {"role": "user", "content": submission}
                    ]
                    response = client.chat.completions.create(messages=message, model=gpt_model, temperature=0.2, max_tokens=1000, top_p=1, frequency_penalty=0, presence_penalty=0)
                    result = response.choices[0].message.content
                    time.sleep(8) # A sleep to avoid getting rate limited by token limit by OpenAI
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
