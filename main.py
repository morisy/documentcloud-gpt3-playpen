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
                ["document_title", "url", "relevance", "certainty", "reason", "document type", "newsworthiness", "summary"]
            )
            
            investigation = self.data.get("investigation")
            self.set_message(f"Working on analyzing {str(len(self.documents))} documents.")
            
            for doc_id in documents:
                try:
                    document = self.client.documents.get(doc_id)
                    full_text = document.get_page_text(1) # Just starting with page one for now due to API limits.

                    response = openai.Completion.create(
                        model="text-davinci-002",
                        prompt="An investigative reporter is working on the following story:\n\n%s\n\nThey have hundreds of documents to go through, and want to focus on only the ones most likely to be relevant to this particular story. For the following text, in the prompted area, return if a document is \"Relevant\" or \"Irrelevant\". Also return how confident you are in that assessment, as well as a description of why you think that document was relevant or irrelevant for this given story in less than 100 characters. Also, include the type of document you believe it is, how newsworthy the document could be to a seasoned investigative journalist with more context, regardless of topic, and a summary of the documents contents. The Analysis section should always be formatted precisely as it is in the examples, with no extra line breaks and the field on one line and value on the next one.\nExamples\n=======\n\n**Document Text**\n\nHey Matt! Really looking forward to it. That time should work well – I will be coming in and that timing works, but will probably be taking the Commuter Rail and T so no need for a parking voucher. Any recs on places I could set up and work though? Any chance you’d be up for grabbing lunch before hand? Would love to catch up.\n\n-----------\nRelevance:\nIrrelevant\nConfidence:\nModerate Confidence\nReason:\n Document is about getting lunch with colleague.\nType of Document\n:Email\n Newsworthiness:\nNot interesting\nSummary:\nSomeone is writing an email asking about details about an upcoming meeting.\n\n—————\n\n**Document Text**\n\nHey Sarah, did you get a copy of the presentation from that Tesseract company? It looked really interesting, though I don't understand all the technology. - Steve\n\n-----------\nRelevance:\nRelevant\nConfidence:\nModerate Confidence\nReason:\nDiscusses new technology vendor\n\nType of Document\n:Email\nNewsworthiness:\nSomewhat interesting, with more context\nSummary:\nAn email to a person named Sarah, asking for the copy of a presentation from technology vendor Tesseract.\n\n —————\n\n**Document Text**\n\n\"APPROVED FOR RELEASE: 08/31/2001 CIA-RDP86-00513R000928620016-7\nTess seers ea Titi FPR TYEE 1\nCEH i sean IERIE\nBr npn Ae mr mr 71 oes\noT os\n5: | &F pesmi 15H\nae Fir ol\null EES KH.\nsels Sony foe Th nt 0 mb ol\noo! iy Be [eo\nsoll EEE Sn lle\n:: | EEE ee\na Eetirt, ME Erle ee\nie EESTI RETR oe\n[ans I IEEE dy ol me oe\n2 Fin kX\nio OE A eR eo!\n\n-----------\nRelevance:\nIrrelevant\n\nConfidence:\nLow Confidence\nReason:\nText not legible\n-----------\n\n**Document Text**\n\n%s\n\n-----------\nRelevance:"%(investigation, full_text),
                        temperature=0.7,
                        max_tokens=1000,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                        )

                    print(response.choices[0].text)
                    response_list = response.choices[0].text.split("\n")
                    relevance = response_list[-11]
                    certainty = response_list[-9]
                    reason = response_list[-7]
                    doctype = response_list[-5]
                    newsworthiness = response_list[-3]
                    summary = response_list[-1]

                    writer.writerow(
                        [
                            document.title,
                            document.canonical_url,
                            relevance,
                            certainty,
                            doctype,
                            newsworthiness,
                            summary
                        ]
                    )
                except:
                    print("Error, moving on to the next item.")
            self.upload_file(file_)


if __name__ == "__main__":
    GPTPlay().main()
