"""verify_results.py

Verify that all of the expected downloads exist.
"""

import sys
from pathlib import Path


def main(dirname):
    contents = []
    for outfile in Path(dirname).glob('*'):
        with outfile.open() as f:
            contents.append(f.read().split())

    # All files report the same total number of urls to be downloaded
    assert len(set(line[-1] for line in contents)) == 1
    total = int(contents[0][-1])
    print("Expecting {} files".format(total))
    assert set(int(line[0]) for line in contents) == set(range(1, total + 1))
    print("All expected files found")

if __name__ == "__main__":
    dirname = sys.argv[1]
    main(dirname=dirname)
