

class DocScore:

    def __init__(self, doc_id, score):
        self.doc_id = doc_id
        self.score = score

    def __lt__(self, other):
        return self.score > other.score

    def get_doc_id(self):
        return self.doc_id