"""
    GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv
import re
import time

from documentcloud.addon import AddOn


import os
import openai

openai.api_key = os.environ["TOKEN"]

class GPTPlay(AddOn):    
    def main(self):
        documents = []
        # provide at least one document.
        if self.documents:
            self.set_message("Running analysis on selected documents.")
            for document in self.documents:
                documents.append(str(document))
        else:
            self.set_message("Running analysis on search results.")
            search_results = self.client.documents.search(self.query)
            for document in search_results:
                documents.append(str(document.id))
        
        with open("compared_docs.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(
                ["document_title", "url", "text", "output"]
            )
            user_input = self.data.get("prompt").translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          ".":  r"\."})) 

            self.set_message(f"Working on analyzing {str(len(self.documents))} documents.")
            
#            try:
#                value = self.data.get("value")
#                self.set_message("Saving the results as a value on the documents as well as generating CSV.")
#            except:
#                    self.set_message("Preparing to generate a CSV.")
            
            for doc_id in documents:
                print("Beginning document iteration.")
                try:
                    document = self.client.documents.get(doc_id)
#                    full_text = document.get_page_text(1) # Just starting with page one for now due to API limits.
                    full_text = document.get_page_text(1).translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          ".":  r"\."})) 
                    submission="%s\n=========\n%s=========="%(user_input, full_text)
                    print(submission)
                    response = openai.Completion.create(
                        model="text-davinci-002",
                        prompt=submission,
                        temperature=0.7,
                        max_tokens=1000,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                        )
                    print("trying to print OpenAI raw response")
                    print(response.choices[0].text)
                    results = response.choices[0].text
   
#                    try:
#                        response = results
#                        response = results.split("Result: ")[-1]
#                    except:
#                        print("Extracting results failed.")
                        
                    writer.writerow(
                        [
                            document.title,
                            document.canonical_url,
                            full_text,
                            results
                        ]
                    )
#                    if value: come back to allowing saving as a tag
                        
                except:
                    print("Error, moving on to the next item.")
            self.upload_file(file_)


if __name__ == "__main__":
    GPTPlay().main()
