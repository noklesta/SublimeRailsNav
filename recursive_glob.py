# Inspired by http://stackoverflow.com/a/2186639

import os
import re


def rglob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = filter(lambda x: re.search(pattern, x), files)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results
