import datetime as dt
from collections import defaultdict

class ResponseCache(object):
    def __init__(self):
        self.record = []
        self.index = defaultdict(list)
        self.last_question = None
        self.last_answer = None
        self.last_time = None

    def clean(self):
        del self.record[:]
        del self.index
        self.record = []
        self.index = defaultdict(list)
        self.last_question = None
        self.last_answer = None
        self.last_time = None

    def _norm(self, s):
        s = s.lower().strip()
        s = s.replace(',', ' ')
        s = s.replace('.', ' ')
        s = ' '.join(s.split()) # remove consecutive spaces
        return s

    def check(self, question, answer):
        if self._norm(answer) == self.last_answer:
            return False
        if self.contain(question, answer):
            return False
        return True

    def add(self, question, answer, datetime=None):
        question = self._norm(question)
        answer = self._norm(answer)
        time = datetime or dt.datetime.now()
        self.record.append({
            'Datetime': time,
            'Question': question,
            'Answer': answer
        })
        self.index[question].append(len(self.record)-1)
        self.last_question = question
        self.last_answer = answer
        self.last_time = time

    def contain(self, question, answer):
        question=self._norm(question)
        answer=self._norm(answer)
        records = self._get_records(question)
        answers = [r['Answer'] for r in records]
        return answer in answers

    def _get_records(self, question):
        question=self._norm(question)
        records = [self.record[i] for i in self.index[question]]
        return records

    def _weight_records(self, question):
        records = self._get_records(question)
        answers = [r['Answer'] for r in records]
        now = dt.datetime.now()
        weights = [sum([(now-r['Datetime']).seconds>600, len(r['Answer'])<20, answers.count(r['Answer'])<2]) for r in records]
        return weights

    def get_best_response(self, question):
        weights = self._weight_records(question)
        if weights:
            idx = weights.index(max(weights))
            return self.record[idx]['Answer']

    def dump(self, fname):
        import csv
        with open(fname, 'w') as f:
            writer = csv.DictWriter(f, ['Datetime', 'Question', 'Answer'], extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.record)

if __name__ == '__main__':
    cache = ResponseCache()
    cache.add('a', 'hi', dt.datetime(2016, 4, 22, 12, 0, 0))
    cache.add('a', 'hi there', dt.datetime(2016, 4, 22, 12, 30, 0))
    cache.add('a', 'how are you', dt.datetime(2016, 4, 22, 12, 30, 0))
    cache.add('a', 'hi there', dt.datetime(2016, 4, 22, 12, 30, 0))
    cache.add('a', 'how are you', dt.datetime(2016, 4, 22, 12, 32, 0))
    cache.add('a', 'how are you', dt.datetime(2016, 4, 22, 12, 32, 0))
    print cache.get_best_response('a')
    cache.dump('tmp')
    print cache.get_best_response('a')
    cache.dump('tmp')
