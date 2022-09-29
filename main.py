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
        documents = self.get_documents()
        
        with open("compared_docs.csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(
                ["document_title", "url", "relevance", "certainty", "reason", "document type", "newsworthiness", "summary"]
            )
            
            investigation = self.data.get("investigation").translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          ".":  r"\."}))            
            self.set_message(f"Working on analyzing {str(len(self.documents))} documents.")
            
            for doc_id in documents:
                try:
                    document = self.client.documents.get(doc_id)
                    full_text = document.get_page_text(1) # Just starting with page one for now due to API limits.

                    response = openai.Completion.create(
                        model="text-davinci-002",
                        prompt="An investigative reporter is working on the following story:\r\n\r\n%s\r\n\r\nThey have hundreds of documents to go through, and want to focus on only the ones most likely to be relevant to this particular story. For the following text, in the prompted area, return if a document is \"Relevant\" or \"Irrelevant\". Also return how confident you are in that assessment, as well as a description of why you think that document was relevant or irrelevant for this given story in less than 100 characters. Also, include the type of document you believe it is, how newsworthy the document could be to a seasoned investigative journalist with more context, regardless of topic, and a summary of the documents contents.\r\n\r\nExamples:\r\n=================\r\n**Document Text**\r\n=================\r\n\r\nHey Matt! Really looking forward to it. That time should work well – I will be coming in and that timing works, but will probably be taking the Commuter Rail and T so no need for a parking voucher. Any recs on places I could set up and work though? Any chance you’d be up for grabbing lunch before hand? Would love to catch up.\r\n\r\n============\r\n**Analysis**\r\n============\r\n\r\nRelevance: Irrelevant\r\nConfidence: Moderate\r\nReason: Document is about getting lunch with colleague.\r\nType of Document: Email\r\nNewsworthiness: Not interesting\r\nSummary: Someone is writing an email asking about details about an upcoming meeting.\r\n\r\n=================\r\n**Document Text**\r\n=================\r\n\r\nHey Sarah, did you get a copy of the presentation from that Tesseract company? It looked really interesting, though I don\'t understand all the technology. - Steve\r\n\r\n============\r\n**Analysis**\r\n============\r\n\r\nRelevance: Relevant\r\nConfidence: Moderate\r\nReason: Document indicates that colleagues are exchanging materials about a technology company.\r\nType of Document: Email\r\nNewsworthiness: Potentially interesting.\r\nSummary: One colleague is writing to another for materials from Tesseract, a technology company that recently presented to them.\r\n\r\n=================\r\n**Document Text**\r\n=================\r\n\r\n\\\"APPROVED FOR RELEASE: 08/31/2001 CIA-RDP86-00513R000928620016-7\r\nTess seers ea Titi FPR TYEE 1\r\nCEH i sean IERIE\r\nBr npn Ae mr mr 71 oes\r\noT os\r\n5: | &F pesmi 15H\r\nae Fir ol\r\null EES KH.\r\nsels Sony foe Th nt 0 mb ol\r\noo! iy Be [eo\r\nsoll EEE Sn lle\r\n:: | EEE ee\r\na Eetirt, ME Erle ee\r\nie EESTI RETR oe\r\n[ans I IEEE dy ol me oe\r\n2 Fin kX\r\nio OE A eR eo!\r\n\r\n============\r\n**Analysis**\r\n============\r\n\r\nRelevance: Irrelevant\r\nConfidence: Low\r\nReason: Document is mostly illegible, but appears to be a poorly scanned CIA document.\r\nType of Document: Unknown\r\nNewsworthiness: Unknown\r\nSummary: A memo line indicates an approved for release document. Unfortunately, nothing else is intelligible.\r\n\r\n=================\r\n**Document Text**\r\n=================\r\n\r\n%s\r\n\r\n============\r\n**Analysis**\r\n============\r\n\r\n"%(investigation, full_text),
                        temperature=0.7,
                        max_tokens=1000,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                        )

                    print(response.choices[0].text)
                    results = response.choices[0].text
   
                    try:
                        relevance = results.split("Relevance: ")[1].split("Confidence")[0]
                        print("Relevance saved")
                        certainty = results.split("Confidence: ")[1].split("\nReason")[0]
                        reason = results.split("Reason: ")[1].split("\nType of Document")[0]
                        doctype = results.split("Type of Document: ")[1].split("\n")[0]
                        newsworthiness = results.split("Newsworthiness: ")[1].split("\n")[0]
                        summary = results.split("Summary: ")[-1]
                    except:
                        print("Extracting results failed.")
                        
                    writer.writerow(
                        [
                            document.title,
                            document.canonical_url,
                            relevance,
                            certainty,
                            reason,
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
