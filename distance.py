from ngram import NGram
import string
from numpy import dot
from numpy.linalg import norm
from array import array

class Distance():

    def __init__(self, str1, str2):
        self.str1 = str1
        self.str2 = str2


    def JaccardDist(self):
        str1 = set(self.str1.split())
        str2 = set(self.str2.split())
        return float(len(str1 & str2)) / len(str1 | str2)


    def ngram(self, n):
        return  NGram.compare(self.str1.lower(), self.str2.lower(), N=n)


    def levenshtein(self, max_dist=-1, normalized=False):

        if normalized:
            return self.nlevenshtein(method=1)

        if self.str1 == self.str2:
            return 0

        len1, len2 = len(self.str1), len(self.str2)
        if max_dist >= 0 and abs(len1 - len2) > max_dist:
            return -1
        if len1 == 0:
            return len2
        if len2 == 0:
            return len1
        if len1 < len2:
            len1, len2 = len2, len1
            self.str1, self.str2 = self.str2, self.str1

        column = array('L', range(len2 + 1))

        for x in range(1, len1 + 1):
            column[0] = x
            last = x - 1
            for y in range(1, len2 + 1):
                old = column[y]
                cost = int(self.str1[x - 1] != self.str2[y - 1])
                column[y] = min(column[y] + 1, column[y - 1] + 1, last + cost)
                last = old
            if max_dist >= 0 and min(column) > max_dist:
                return -1

        if max_dist >= 0 and column[len2] > max_dist:
            # stay consistent, even if we have the exact distance
            return -1
        return column[len2]

    # Normailized edit distance which returns distance between two strings in range 0 to 1
    def nlevenshtein(self,  method=1):
        if self.str1 == self.str2:
            return 0.0
        len1, len2 = len(self.str1), len(self.str2)
        if len1 == 0 or len2 == 0:
            return 1.0
        if len1 < len2:  # minimize the arrays size
            len1, len2 = len2, len1
            self.str1, self.str2 = self.str2, self.str1

        if method == 1:
            return self.levenshtein() / float(len1)
        if method != 2:
            raise ValueError("expected either 1 or 2 for `method` parameter")

        column = array('L', range(len2 + 1))
        length = array('L', range(len2 + 1))

        for x in range(1, len1 + 1):

            column[0] = length[0] = x
            last = llast = x - 1

            for y in range(1, len2 + 1):
                # dist
                old = column[y]
                ic = column[y - 1] + 1
                dc = column[y] + 1
                rc = last + (self.str1[x - 1] != self.str2[y - 1])
                column[y] = min(ic, dc, rc)
                last = old

                # length
                lold = length[y]
                lic = length[y - 1] + 1 if ic == column[y] else 0
                ldc = length[y] + 1 if dc == column[y] else 0
                lrc = llast + 1 if rc == column[y] else 0
                length[y] = max(ldc, lic, lrc)
                llast = lold
        return column[y] / float(length[y])

    def matching_func(self, weights):
        jaccard = self.JaccardDist()
        ngrams = self.ngram(n=1)
        editdist = 1 - self.nlevenshtein() # Normalize as other functions
        distancevector = [jaccard, ngrams, editdist]
        weightedaverage = sum(x*y for x,y in zip(weights, distancevector))
        return weightedaverage




if __name__ == '__main__':
    text1 = 'ABCD GHIJKLMNO UML QRTSUVWXYZ'
    text2 = 'UML'
    obj = Distance(text2, text1)
    weights = [0.25, 0.5, 0.25] # weight your preference method according to the sting model you have
    print(obj.matching_func(weights))



