
import requests

API_KEY = 'c9187cfd41d4c6496be780048b47904e'
HEADERS = {'X-ELS-APIKey': API_KEY}

def get_eid(doi):
    url = f'https://api.elsevier.com/content/search/scopus?query=DOI({doi})&field=eid'
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    entries = data.get('search-results', {}).get('entry', [])
    if entries:
        return entries[0].get('eid')
    return None

def get_citing_documents(eid):
    url = f'https://api.elsevier.com/content/abstract/citations?scopus_id={eid}'
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    # Process data to extract citing documents
    # ...
    return data

# Example usage
doi = '10.48161/qaj.v4n3a699'
eid = get_eid(doi)
if eid:
    citing_docs = get_citing_documents(eid)
    # Further processing to determine quartile rankings
    # ...
else:
    print('EID not found for DOI:', doi)
