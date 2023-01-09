import argparse
import os
import logging
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from scipy.sparse import csr_matrix

def get_hits(cov_file_path):
    tree = ET.parse(cov_file_path)
    root = tree.getroot()
    # key: (class_name, method_name, signature)
    # value: hitcount
    hits = {}
    packages = root[1]
    for package in packages:
        for classes in package:
            for _class in classes:
                class_name = _class.attrib["name"]
                methods = _class.find('methods')
                for method in methods:
                    method_name = method.attrib["name"]
                    method_signature = method.attrib["signature"]
                    args_type = method_signature[1:].split(')')[0]
                    method_id = "{}${}<{}>".format(class_name, method_name, args_type)
                    lines = method.find('lines')
                    for line in lines:
                        hits[(method_id, line.attrib["number"])] = int(line.attrib["hits"])
    return hits

def merge(coverage_dir, savepath, sparse=True):
    coverage_dir = os.path.abspath(coverage_dir)
    savepath = os.path.abspath(savepath)
    logging.debug("Coverage dir: {}".format(coverage_dir))
    logging.debug("Output path: {}".format(savepath))

    cov = pd.DataFrame() # Empty Dataframe
    
    if not os.path.exists(coverage_dir):
        raise Exception("No directory exists: {}".format(coverage_dir))

    for test in os.listdir(coverage_dir):
        if test[-4:] != ".xml":
            continue
        lines = cov.index.values.tolist()
        hits = get_hits(os.path.join(coverage_dir, test))
        new_lines = list(set(hits.keys()) - set(lines))
        coverage_vector = []
        for line in lines:
            coverage_vector.append(hits[line] if line in hits else 0)
        test_key = test[:-4].replace("::", ".")
        cov[test_key] = np.array(coverage_vector)
        if new_lines:
            testcases = cov.columns.values.tolist()
            rows = []
            for l in new_lines:
                rows.append([hits[l] if test==test_key else 0 for test in testcases])
            new_rows = pd.DataFrame(
                rows,
                index=new_lines,
                columns=testcases,
            )
            logging.debug("Appending {} new lines".format(len(new_lines)))
            cov = cov.append(new_rows)
        logging.debug("Adding {}: {}".format(test_key, cov.shape))
    if sparse:
        cov = pd.DataFrame.sparse.from_spmatrix(csr_matrix(cov), index=cov.index, columns=cov.columns)
    cov = cov.astype(bool)
    cov.to_pickle(savepath)
    logging.debug("Saved to {}".format(savepath))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("newdir", type=str)
    parser.add_argument("--sparse", "-s", action="store_true",
        help="Save as a sparse matrix if True")
    parser.add_argument("--savepath", "-o", type=str, default="output.pkl",
        help="Path to the output matrix")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    merge(args.newdir, args.savepath, args.sparse)
