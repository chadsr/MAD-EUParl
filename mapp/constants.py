# https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#module-rdflib.namespace
from rdflib import Namespace, Literal
from rdflib.namespace import XSD, RDF, OWL, FOAF
import os

DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

LOG_DIR = os.path.join(DIR, 'logs/')
DATA_DIR = os.path.join(DIR, 'data/')

MAIN_LOG = os.path.join(LOG_DIR, 'europarl.log')

JSON_DIR = os.path.join(DATA_DIR, 'json/')
LD_DIR = os.path.join(DATA_DIR, 'linked_data/')

ONTOLOGY = os.path.join(LD_DIR, 'europarl.ttl')
DATA_OUTPUT = os.path.join(LD_DIR, 'europarl_ds.ttl')
GRAPH_OUTPUT = os.path.join(LD_DIR, 'europarl_graph.ttl')

DIR_MEPS = os.path.join(JSON_DIR, 'mep_chunks')
DIR_DOSSIERS = os.path.join(JSON_DIR, 'dossier_chunks')
DIR_VOTES = os.path.join(JSON_DIR, 'vote_chunks')

DATA_MEP = os.path.join(JSON_DIR, 'ep_meps_current.json')
DATA_VOTES = os.path.join(JSON_DIR, 'ep_votes.json')
DATA_DOSSIER = os.path.join(JSON_DIR, 'ep_dossiers.json')

EXTERNAL_MEP_URIS = os.path.join(JSON_DIR, 'mep_uris.json')
EXTERNAL_PARTY_URIS = os.path.join(JSON_DIR, 'party_uris.json')
EXTERNAL_PLACES_URIS = os.path.join(JSON_DIR, 'places_uris.json')
EXTERNAL_COMMITTEE_URIS = os.path.join(JSON_DIR, 'committee_uris.json')

DICT_COMMITTEES = os.path.join(JSON_DIR, 'dict_committees.json')
DICT_MISC_VOTES = os.path.join(JSON_DIR, 'misc_votes.json')

SPARQL_ENDPOINT = 'http://192.168.1.60:7200/repositories/europarl/statements'

DOWNLOAD_TIMEOUT = 30
DATA_URLS = {DIR_VOTES: 'http://parltrack.euwiki.org/dumps/ep_votes.json.xz',
             DIR_MEPS: 'http://parltrack.euwiki.org/dumps/ep_meps_current.json.xz',
             DIR_DOSSIERS: 'http://parltrack.euwiki.org/dumps/ep_dossiers.json.xz'}

DATABASE = 'http://localhost:7200/europarl#'  # Database endpoint
NAMESPACE = DATABASE

URL_DBPEDIA_LOOKUP = 'http://lookup.dbpedia.org/api/search/KeywordSearch?'
URL_DBPEDIA_SPOTLIGHT = 'http://localhost:2222/rest/annotate'

VOTE_ACTIVITIES = ['results of vote in parliament', 'r\u00e9sultat du vote au parlement']

FILTER_PERSON = {
    'policy': "whitelist",
    'types': "DBpedia:Person",
    'coreferenceResolution': False
}
FILTER_PLACE = {
    'policy': "whitelist",
    'types': "DBpedia:Place",
    'coreferenceResolution': False
}
FILTER_COUNTRY = {
    'policy': "whitelist",
    'types': "DBpedia:Country",
    'coreferenceResolution': False
}
FILTER_POLITICAL_PARTY = {
    'policy': "whitelist",
    'types': "DBpedia:PoliticalParty,DBpedia:Organisation",
    'coreferenceResolution': False
}


ont = NAMESPACE
ONT = Namespace(ont)
PREFIX = 'epv'

lp = 'http://purl.org/linkedpolitics/'
LP = Namespace(lp)
lpv = 'http://purl.org/linkedpolitics/vocabulary/'
LPV = Namespace(lpv)

dbo = 'http://dbpedia.org/ontology/'
DBO = Namespace(dbo)
dbr = 'http://dbpedia.org/resource/'
DBR = Namespace(dbr)
dbp = 'http://dbpedia.org/property/'
DBP = Namespace(dbp)

MEP = ONT['MEP']
DOSSIER = ONT['Dossier']
ACTIVITY = ONT['Activity']
PROCESSED_BY = ONT['processedBy']
HAS_ACTIVITY = ONT['activity']
GEO_AREA = ONT['geoArea']

START_DATE = ONT['startDate']
END_DATE = ONT['endDate']

DOSSIER_TITLE = ONT['dossierTitle']
REPORT_TITLE = ONT['reportTitle']
ACTIVITY_TITLE = ONT['activityTitle']

DOCUMENT = ONT['Document']
REPORT = ONT['Report']
DOCUMENT_TITLE = ONT['documentTitlte']
VOTE_TITLE = ONT['voteTitle']
COMMITTEE_TITLE = ONT['committeeTitle']

HAS_DOC = ONT['document']

IS_RESPONSIBLE = ONT['isResponsibleIn']
IS_INVOLVED = ONT['isInvolvedIn']
HAS_RAPPORTEUR = ONT['rapporteur']

PARLIAMENT_VOTE = ONT['VoteInParliament']
IS_VOTE_FOR = ONT['voteOn']
REACTION_BY = ONT['reactionBy']
REACTION_TO = ONT['reactionTo']
ABSTAIN = ONT['Abstain']
VOTE_FOR = ONT['VoteFor']
VOTE_AGAINST = ONT['VoteAgainst']

HAS_BODY = ONT['body']

POLITICAL_GROUP = ONT['PoliticalGroup']
INSTITUTION = ONT['Institution']
COMMITTEE = ONT['Committee']

REPRESENTS_COUNTRY = ONT['representsCountry']

BASED_ON_REPORT = ONT['basedOnReport']
IS_WITHIN = ONT['within']
HAS_MEMBERSHIP = ONT['membership']

GENDER = FOAF.gender
MALE = Literal('male', datatype=XSD.string)
FEMALE = Literal('female', datatype=XSD.string)

EUROPEAN_PARLIAMENT_GROUP = DBO['europeanParliamentGroup']
IN_LEGISLATURE = DBO['politicalPartyInLegislature']
POLITICAL_PARTY = DBO['PoliticalParty']
LEGISLATURE = DBO['Legislature']
ORGANISATION = DBO['Organisation']
OFFICE = DBP['office']
MEMBER_OF_EU = DBR['Member_of_the_European_Parliament']
THUMBNAIL = DBO['thumbnail']
IMAGE = DBO['Image']

FULL_NAME = FOAF.name
BIRTH_DATE = DBO['birthDate']
BIRTH_PLACE = DBO['birthPlace']
DEATH_DATE = DBO['deathDate']

URI = XSD.anyURI
STRING = XSD.string
DATE = XSD.date
BOOLEAN = XSD.boolean

TYPE = RDF.type
SAME_AS = OWL.sameAs

MEMBER = ONT['Membership']
SUBSTITUTE = ONT['Substitute']
DEPUTY_TREASURER = ONT['DeputyTreasurer']
VICE_CHAIR = ONT['ViceChair']
CO_CHAIR = ONT['CoChair']
BUREAU_VICE_CHAIR = ONT['ViceChairOfTheBureau']
CO_TREASURER = ONT['CoTreasurer']
DEPUTY_CHAIR = ONT['DeputyChair']
OBSERVER = ONT['Observer']
SUBSTITUTE_OBSERVER = ONT['SubstituteObserver']
BUREAU_CHAIR = ONT['ChairOfTheBureau']
CHAIR = ONT['Chair']
PRESIDENT = ONT['President']
TREASURER = ONT['Treasurer']
BUREAU_MEMBER = ONT['MemberOfTheBureau']
MEMBERSHIPS = {
    'Member': MEMBER,
    'Member of the Bureau': BUREAU_MEMBER,
    'Vice-Chair': VICE_CHAIR,
    'Treasurer': TREASURER,
    'President': PRESIDENT,
    'Chair': CHAIR,
    'Co-Chair': CO_CHAIR,
    'Chair of the Bureau': BUREAU_CHAIR,
    'Co-treasurer': CO_TREASURER,
    'Observer': OBSERVER,
    'Deputy Chair': DEPUTY_CHAIR,
    'Vice-Chair/Member of the Bureau': BUREAU_VICE_CHAIR,
    'Deputy Treasurer': DEPUTY_TREASURER,
    'Substitute': SUBSTITUTE,
    'Substitute observer': SUBSTITUTE_OBSERVER
}

EUROPEAN_PARLIAMENT_DBR = DBR['European_Parliament']
EUROPEAN_COUNCIL_DBR = DBR['European_Council']
EUROPEAN_COMMISION_DBR = DBR['European_Commission']
EUROPEAN_CENTRAL_BANK_DBR = DBR['European_Central_Bank']
EUROPEAN_CENTRAL_BANK = ONT['european_central_bank']
EUROPEAN_PARLIAMENT = ONT['european_parliament']
EUROPEAN_COUNCIL = ONT['european_council']
EUROPEAN_COMMISSION = ONT['european_commission']
EUROPEAN_ECONOMIC_SOCIAL_COMMITTEE = ONT['european_economic_and_social_committee']
EUROPEAN_COURT_OF_AUDITORS = ONT['european_court_of_auditors']
EUROPEAN_COURT_OF_AUDITORS_DBR = DBR['Court_of_Auditors']
EUROPEAN_COMMITTEE_OF_REGIONS = ONT['european_committee_of_regions']
EUROPEAN_COMMITTEE_OF_REGIONS_DBR = DBR['Committee_of_the_Regions']
EUROPEAN_DATA_PROTECTION_SUPERVISOR = ONT['european_data_protection_supervisor']
EUROPEAN_DATA_PROTECTION_SUPERVISOR_DBR = DBR['European_Data_Protection_Supervisor']
EUROPEAN_COMMUNITIES_COURT_OF_JUSTICE = ONT['european_communities_court_of_justice']
EUROPEAN_UNION_COURT_OF_JUSTICE = ONT['european_court_of_justice']
EUROPEAN_UNION_COURT_OF_JUSTICE_DBR = DBR['European_Court_of_Justice']

__EP__ = {
    PREFIX: EUROPEAN_PARLIAMENT,
    'dbpedia': EUROPEAN_PARLIAMENT_DBR
}

__EC__ = {
    PREFIX: EUROPEAN_COMMISSION,
    'dbpedia': EUROPEAN_COMMISION_DBR
}

__CSL__ = {
    PREFIX: EUROPEAN_COUNCIL,
    'dbpedia': EUROPEAN_COUNCIL_DBR
}

__ESOC__ = {
    PREFIX: EUROPEAN_ECONOMIC_SOCIAL_COMMITTEE,
    'dbpedia': None
}

__COA__ = {
    PREFIX: EUROPEAN_COURT_OF_AUDITORS,
    'dbpedia': EUROPEAN_COURT_OF_AUDITORS_DBR
}

__EDPS__ = {
    PREFIX: EUROPEAN_DATA_PROTECTION_SUPERVISOR,
    'dbpedia': EUROPEAN_DATA_PROTECTION_SUPERVISOR_DBR
}

__CJEU__ = {
    PREFIX: EUROPEAN_UNION_COURT_OF_JUSTICE,
    'dbpedia': EUROPEAN_UNION_COURT_OF_JUSTICE_DBR
}

__CJEC__ = {
    PREFIX: EUROPEAN_COMMUNITIES_COURT_OF_JUSTICE,
    'dbpedia': None
}

__COR__ = {
    PREFIX: EUROPEAN_COMMITTEE_OF_REGIONS,
    'dbpedia': EUROPEAN_COMMITTEE_OF_REGIONS_DBR
}

__ECB__ = {
    PREFIX: EUROPEAN_CENTRAL_BANK,
    'dbpedia': EUROPEAN_CENTRAL_BANK_DBR
}

__ALL__ = {  # This seems to denote "Additional Information"?
    PREFIX: None,
    'dbpedia': None
}

BODIES = {
    'all': [__ALL__],
    'EP': [__EP__],
    'EC': [__EC__],
    'CSL': [__CSL__],
    'ESOC': [__ESOC__],
    'EDPS': [__EDPS__],
    'CJEC': [__CJEC__],
    'CJEU': [__CJEU__],
    'CoA': [__COA__],
    'CoR': [__COR__],
    'CotR': [__COR__],
    'ECB': [__ECB__],
    'EP/CSL': [__EP__, __CSL__]
}

VOTES = {'Abstain': ABSTAIN, 'For': VOTE_FOR, 'Against': VOTE_AGAINST}
