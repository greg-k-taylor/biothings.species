
def parse_geneinfo_taxid(fileh):

    for line in fileh:
        if line.startswith("#"):
            # skip header
            continue
        taxid = line.split("\t")[0]
        yield {"_id" : taxid}

