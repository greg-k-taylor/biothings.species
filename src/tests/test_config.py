###################################################################################
# test settings
###################################################################################

# biothings specific options - these should be identical to the production server 
# you are testing for...  For example, JSONLD_CONTEXT_PATH should point to a file
# with contents identical to the file pointed to by JSONLD_CONTEXT_PATH on the 
# production server (if your intention is to test the production server).

JSONLD_CONTEXT_URL = ""
API_VERSION = "v1"
QUERY_ENDPOINT = "query"
ANNOTATION_ENDPOINT = "species"

# This is the name of the environment variable to load for testing
HOST_ENVAR_NAME = 'MS_HOST'
# This is the URL of the production server, if the above envar can't be loaded, nosetest defaults to this
NOSETEST_DEFAULT_URL = "http://s.biothings.io"

###################################################################################
# Nosetests used in tests.py, fill these in with IDs/queries.
###################################################################################

# This is the test for fields in the annotation object.  You should pick an ID
# with a representative set of root level annotations associated with it.
ANNOTATION_OBJECT_ID = '9606'
# This is the list of expected keys that the JSON object returned by the ID above
ANNOTATION_OBJECT_EXPECTED_ATTRIBUTE_LIST = ['_id', '_version', 'common_name', 'taxid', 'scientific_name', 'lineage']

# -----------------------------------------------------------------------------------

# This is a list of IDs (& options) to test a GET to the annotation endpoint
ANNOTATION_GET_IDS = ['9606', 
                      '9606?fields=lineage&callback=mycallback', 
                      '9606?fields=common_name,taxid', 
                      '9606?jsonld=true'
                     ] 
ANNOTATION_GET_MSGPACK = ['9606?msgpack=true',
                          '9606?fields=common_name&msgpack=true']
ANNOTATION_GET_JSONLD = ['9606?jsonld=true']
ANNOTATION_GET_FIELDS = ['9606?fields=lineage',
                         '9606?fields=common_name,taxid']
ANNOTATION_GET_FILTER = ['9606?filter=lineage',
                         '9606?filter=common_name,taxid']

# -----------------------------------------------------------------------------------

# This is a list of dictionaries to test a POST to the annotation endpoint

ANNOTATION_POST_DATA = [{'ids': '9606'},
                        {'ids': '9606,10090'},
                        {'ids': '9606,10090', 'fields': 'common_name'},
                        {'ids': '9606,10090', 'jsonld': 'true'}
                        ]

# -----------------------------------------------------------------------------------

# This is a list of query strings (& options to test a GET to the query endpoint
QUERY_GETS = ['9606',
              'homo%20sapiens',
              'taxid:[9000%20TO%2010000]&fields=taxid,common_name',
              'taxid:[9000%20TO%2010000]&fields=taxid&callback=mycallback',
              'taxid:[7000%20TO%2010000]&fields=taxid&fetch_all=true',
              'taxid:[9000%20TO%2010000]&fields=taxid&facets=taxid',
              'human&size=2000',
              ]
              

# -----------------------------------------------------------------------------------

# This is a list of dictionaries to test a POST to the query endpoint
QUERY_POST_DATA = [{'q': 'homo sapiens, mus musculus', 'scopes':'scientific_name'},
                   {'q': '9606,10090', 'scopes': 'taxid'},
                   {'q': '9606,10090', 'scopes': 'taxid', 'fields': 'common_name'},
                   {'q': '9606,10090', 'scopes': 'taxid', 'fields': 'common_name', 'jsonld':'true'}
                  ]

# -----------------------------------------------------------------------------------

# This is the minimum number of unique field keys (from /metadata/fields)
MINIMUM_NUMBER_OF_ACCEPTABLE_FIELDS = 7

# -----------------------------------------------------------------------------------

# This is the minimum number of unique field keys (from /metadata/fields)
TEST_FIELDS_GET_FIELDS_ENDPOINT = ['common_name', 'genbank_common_name','has_gene', 'lineage', 'parent_taxid', 'rank']

# -----------------------------------------------------------------------------------

# Any additional fields added for check_fields subset test
CHECK_FIELDS_SUBSET_ADDITIONAL_FIELDS = []
