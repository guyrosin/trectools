# External libraries
import sarge
import os

from trectools import TrecRun


class TrecTerrier:

    def __init__(self, bin_path):
        self.bin_path = bin_path

    def run(self, index, topics, debug=True, model="PL2", ndocs=1000, result_dir=None, result_file="trec_terrier.run",
            terrierc=None, qexp=False, expTerms=5, expDocs=3, expModel="Bo1", showoutput=False):

        if result_dir is None:
            # Current dir is used if result_dir is not set
            result_dir = os.getcwd()

        program = f"{self.bin_path}/terrier.bat" if os.name == 'nt' else f"{self.bin_path}/terrier"
        cmd = f"{program} batchretrieve -t {topics} -w {model} -Dtrec.results={result_dir} -o {result_file}"

        cmd += f" -Dmatching.retrieved_set_size={ndocs} -Dtrec.output.format.length={ndocs} "

        if terrierc is not None:
            cmd += f" -c c:{terrierc} "

        if qexp:
            cmd += f" -q -Dexpansion.terms={expTerms} -Dexpansion.documents={expDocs} -c qemodel:{expModel}"

        if index:
            cmd += f" -I {index}/data.properties"

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
    # tt = TrecTerrier(bin_path="/data/palotti/terrier/terrier-5.1/bin/terrier")
    # tr = tt.run(index="/data/palotti/terrier/terrier-5.1/var/index", topics="/data/palotti/trec_cds/metamap/default_summary.xml.gz", qexp=False)
