import traceback
import re
from collections import defaultdict
from tqdm import tqdm
from common import *
from phrase_finder import PhraseFinder
from log.Logger import Logger

logger = Logger()
phrase_finder = PhraseFinder()


class OntologyGenerator(object):
    def __init__(self, stop_tokens):
        self.stop_tokens = stop_tokens
        pass

    @staticmethod
    def filter_substrings(node_names):
        new_node_names = copy.deepcopy(node_names)
        for node_1 in node_names:
            node_1_stripped = node_1.strip()
            for node_2 in node_names:
                node_2_stripped = node_2.strip()
                try:
                    if node_1_stripped != node_2_stripped:
                        if node_2_stripped in node_1_stripped:
                            new_node_names.remove(node_2)
                        elif node_1_stripped in node_2_stripped:
                            new_node_names.remove(node_1)
                except Exception:
                    pass
        return new_node_names

    def process_qna(self, phrases, uni_tokens, verbs, qna_object_map):
        most_commons_terms = dict()
        quest_ontology_map = defaultdict(dict)
        logger.info('Initiated ontology generation')
        try:
            for ques_id, qna_object in tqdm(qna_object_map.items()):
                ques = qna_object.normalized_ques
                quest_ontology_map[ques_id]['question'] = qna_object.question
                tags = ''
                terms = list()
                q = copy.deepcopy(ques)
                doc = nlp(q)
                doc = " ".join([t.lemma_ if t.lemma_ != "-PRON-" else t.text for t in doc])

                most_commons_terms.update(phrases.most_common())
                most_commons_terms.update(uni_tokens.most_common())
                most_commons_terms.update(verbs.most_common())
                ind = 0
                for term, cnt in phrases.most_common():
                    ind += 1
                    if cnt == 1:
                        break
                    if term in self.stop_tokens:
                        continue
                    try:
                        regex = re.compile("\\b" + term + "\\b")
                        if re.findall(regex, doc) and cnt > 1:
                            doc = re.sub(regex, "~~~~", doc)
                            terms.append(term)
                    except Exception:
                        print(traceback.format_exc())

                for term, cnt in uni_tokens.most_common():
                    ind += 1
                    if cnt == 1:
                        break
                    if term in self.stop_tokens:
                        continue
                    try:
                        regex = re.compile("\\b" + term + "\\b")
                        if re.findall(regex, doc):
                            doc = re.sub(regex, "~~~~", doc)
                            terms.append(term)
                    except Exception:
                        print(traceback.format_exc())

                for term, cnt in verbs.most_common():
                    ind += 1
                    if cnt == 1:
                        break
                    try:
                        regex = re.compile("\\b" + term + "\\b")
                        if re.findall(regex, doc):
                            tags=term
                    except Exception:
                        pass

                terms = sorted(self.filter_substrings(terms), key=lambda x: most_commons_terms[x]) + [BOT_NAME]
                quest_ontology_map[ques_id]['terms'] = terms
                tags = [tags] if tags else []
                quest_ontology_map[ques_id]['tags'] = tags
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception('Failed in generating ontology')

        return quest_ontology_map

# todo - seperate trigrams and bigrams, apply stashed changes