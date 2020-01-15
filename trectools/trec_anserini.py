# External libraries
import sarge
import os

from trectools import TrecRun

"""
Search using Anserini.
See arguments here: https://github.com/castorini/anserini/blob/master/src/main/java/io/anserini/search/SearchArgs.java
"""


class TrecAnserini:

    def __init__(self, bin_path):
        self.bin_path = bin_path

    def run(self, index, topics, debug=True, model="bm25", ndocs=1000, result_dir=None, result_file="trec_anserini.run",
            expModel=None, expTerms=5, expDocs=3, showoutput=False):

        if result_dir is None:
            # Current dir is used if result_dir is not set
            result_dir = os.getcwd()

        program = f"{self.bin_path}/SearchCollection.bat" if os.name == 'nt' else f"{self.bin_path}/SearchCollection"
        cmd = f"{program} -index {index} -topicreader Trec -topics {topics} -{model} " \
              f"-output {os.path.join(result_dir, result_file)}"

        cmd += f" -hits={ndocs}"

        if expModel:
            cmd += f" -{expModel} -{expModel}.fbTerms={expTerms} -{expModel}.fbDocs={expDocs}"

        if not showoutput:
            cmd += f" > {os.devnull} 2> {os.devnull}"

        if debug:
            print(f"Running: {cmd} ")

        r = sarge.run(cmd).returncode

        if r == 0:
            return TrecRun(os.path.join(result_dir, result_file))
        else:
            print(f"ERROR with command {cmd}")
            return None


if __name__ == '__main__':
    pass
