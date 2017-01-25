def parse_uniprot_speclist(uniprot_speclist):
    '''
    uniprot_speclist is a file-like object yielding 'speclist.txt'
    '''
    while True:
        line = next(uniprot_speclist)
        if line.startswith('_____'):
            break

    for line in uniprot_speclist:
        if line.count('N='):
            organism_name = line.split('N=')[-1].strip().lower()
            taxonomy_id = int(line.split()[2][:-1])
            doc = {"_id" : taxonomy_id, 'uniprot_name': organism_name, 'taxid': taxonomy_id}
            yield doc

