"""
    GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv
import re
import time

from documentcloud.addon import AddOn


import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


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
                ["document_title", "url", "relevance", "reason"]
            )
            
            investigation = self.client.documents.get(self.data.get("investigation"))
            self.set_message(f"Working on analyzing {str(len(self.documents))} documents.")
            
            for doc_id in documents:
                document = self.client.documents.get(doc_id)
                full_text = document.full_text

                response = openai.Completion.create(
                    model="text-davinci-002",
                    prompt="An investigative reporter is working on the following story:\n\n%s\n\nThey have hundreds of documents to go through, and want to focus on only the ones most likely to be relevant. For the following text, in the prompted area, return if a document is \"Relevant\" or \"Irrelevant\". Also return how confident you are in that assessment, as well as a description of why you think that document was relevant or irrelevant in less than 100 characters.\n\nExamples\n=======\n\n**Document Text**\n\nHey Matt! Really looking forward to it. That time should work well – I will be coming in and that timing works, but will probably be taking the Commuter Rail and T so no need for a parking voucher. Any recs on places I could set up and work though? Any chance you’d be up for grabbing lunch before hand? Would love to catch up.\n\n-----------\nRelevance: Irrelevant\nReason: Document is about getting lunch with colleague.\n-----------\n\n**Document Text**\n\nHey Sarah, did you get a copy of the presentation from that Tesseract company? It looked really interesting, though I don't understand all the technology. - Steve\n\n-----------\nRelevance: Relevant\nReason: Discusses new technology vendor\n-----------\n\n**Document Text**\n\n\"APPROVED FOR RELEASE: 08/31/2001 CIA-RDP86-00513R000928620016-7\nTess seers ea Titi FPR TYEE 1\nCEH i sean IERIE\nBr npn Ae mr mr 71 oes\noT os\n5: | &F pesmi 15H\nae Fir ol\null EES KH.\nsels Sony foe Th nt 0 mb ol\noo! iy Be [eo\nsoll EEE Sn lle\n:: | EEE ee\na Eetirt, ME Erle ee\nie EESTI RETR oe\n[ans I IEEE dy ol me oe\n2 Fin kX\nio OE A eR eo!\n\n-----------\nRelevance: Irrelevant\nReason: Text not legible\n-----------\n\n**Document Text**\n\n%s\n\n-----------\nRelevance:"%(investigation, full_text),
                    temperature=0.7,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                    )

                writer.writerow(
                    [
                        document.title,
                        document.canonical_url,
                        response.splitlines()[-2],
                        response.splitlines()[-1]
                    ]
                )
            self.upload_file(file_)


if __name__ == "__main__":
    GPTPlay().main()
