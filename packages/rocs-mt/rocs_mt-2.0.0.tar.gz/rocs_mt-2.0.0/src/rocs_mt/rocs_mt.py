#!/usr/bin/python
from datasets import load_dataset
from typing import Literal
import json

_PARTITIONS = Literal["manseg_norm", "manseg_raw", "nlseg_raw"]
_SRC = Literal["en_norm", "en_raw"]
_TRG = Literal["fr", "de", "cs", "uk", "ru"]

class RoCS_MT_segment(object):
    def __init__(self, record, raw=False):

        if raw:
            for key in ["post_id", "segment_id", "text_type", "raw_segment" \
                        "normalised_segment", "source_attributes", "translation_notes" \
                        "normalisation_span_annotations", "unsegmented_raw_doc", \
                        "fr_translations", "cs_translations", "de_translations" \
                        "ru_translations", "uk_translations"]:
                setattr(self, key, record.get(key, None))
            
        else:
            for key, value in record.items():
                setattr(self, key, value)

        
    def get_parallel(self, src:_SRC, trg:_TRG):
        src_segment = {"en_norm": self.normalised_segment,
                       "en_raw": self.raw_segment}[src]
        ref_segments = getattr(self, f"{lang}_translations")
        ref_texts = [ref_segment["text"] for ref_segment in ref_segments]

        return {"src": src_segment, "ref": ref_texts, "full_record":  dict(self.__dict__)}

    def __repr__(self):
        def short(text, limit=80):
            text = text.replace("\n", " ")
            return text if len(text) <= limit else text[:limit] + "…"

        return (
            f"rocs_mt_segment(\n"
            f"  segment_id={self.segment_id},\n"
            f"  raw_segment='{short(self.raw_segment)}',\n"
            f"  normalised_segment='{short(self.normalised_segment)}',\n"
            f"  fr_translations ({len(self.fr_translations)})='{short(self.fr_translations[0]['text'])}',\n"
            f"  cs_translations ({len(self.cs_translations)})='{short(self.cs_translations[0]['text'])}',\n"
            f"  de_translations ({len(self.de_translations)})='{short(self.de_translations[0]['text'])}',\n"
            f"  ru_translations ({len(self.ru_translations)})='{short(self.ru_translations[0]['text'])}',\n"
            f"  uk_translations ({len(self.uk_translations)})='{short(self.uk_translations[0]['text'])}'\n"
            f"  …\n"
            f")"
        )


class RoCS_MT_dataset(object):

    def __init__(self):
        self.ds = load_dataset("rbawden/RoCS-MT-v2")
        self.manseg = []
        self.nlseg = []
        self.get_records()

    def get_records(self):

        last_doc = None
        for record in self.ds['train']:

            # convert to dictionary format
            for trg_lang in ["fr", "de", "cs", "uk", "ru"]:
                record[f"{trg_lang}_translations"] = json.loads(record[f"{trg_lang}_translations"])
            record["source_attributes"] = json.loads(record["source_attributes"])
            record["translation_notes"] = json.loads(record["translation_notes"])
            record["normalisation_span_annotations"] = json.loads(record["normalisation_span_annotations"])

            # store all records
            self.manseg.append(RoCS_MT_segment(record))

            # add separate newline-separated records
            if last_doc != record["unsegmented_raw_doc"]:
                for sent in record["unsegmented_raw_doc"].split('\n'):
                    if len(sent.strip()) > 0:
                        self.nlseg.append(RoCS_MT_segment({"raw_segment": sent,
                                                           "post_id": record["post_id"],
                                                           "unsegmented_raw_doc": record["unsegmented_raw_doc"],
                                                           "text_type": record["text_type"]}, True))
            last_doc = record["unsegmented_raw_doc"] # keep a track of the last document

            
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    dataset = RoCS_MT_dataset()


    

