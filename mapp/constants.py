# https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#module-rdflib.namespace
from rdflib import Namespace, Literal
from rdflib.namespace import XSD, RDF, OWL, FOAF
import os

DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

LOG_DIR = DIR + '/logs/'
DATA_DIR = DIR + '/data/'

MAIN_LOG = LOG_DIR + 'parlialytics.log'

JSON_DIR = DATA_DIR + 'json/'
LD_DIR = DATA_DIR + 'linked_data/'

DATA_OUTPUT = LD_DIR + 'parlialytics.ttl'
GRAPH_OUTPUT = LD_DIR + 'parltrack-graph.ttl'

DIR_MEPS = os.path.join(JSON_DIR, 'mep_chunks')
DIR_DOSSIERS = os.path.join(JSON_DIR, 'dossier_chunks')
DIR_VOTES = os.path.join(JSON_DIR, 'vote_chunks')

DATA_MEP = JSON_DIR + 'ep_meps_current.json'
DATA_VOTES = JSON_DIR + 'ep_votes.json'
DATA_DOSSIER = JSON_DIR + 'ep_dossiers.json'

EXTERNAL_MEP_URIS = JSON_DIR + 'mep_uris.json'
EXTERNAL_PARTY_URIS = JSON_DIR + 'party_uris.json'
EXTERNAL_PLACES_URIS = JSON_DIR + 'places_uris.json'

DICT_COMMITTEES = JSON_DIR + 'dict_committees.json'
DICT_MISC_VOTES = JSON_DIR + 'misc_votes.json'

SPARQL_ENDPOINT = 'http://localhost:7200/repositories/parlialytics/statements'

DOWNLOAD_TIMEOUT = 30
DATA_URLS = {DIR_VOTES: 'http://parltrack.euwiki.org/dumps/ep_votes.json.xz',
             DIR_MEPS: 'http://parltrack.euwiki.org/dumps/ep_meps_current.json.xz',
             DIR_DOSSIERS: 'http://parltrack.euwiki.org/dumps/ep_dossiers.json.xz'}

DATABASE = 'http://localhost:7200/parlialytics#'  # Database endpoint
NAMESPACE = DATABASE

URL_DBPEDIA_LOOKUP = 'http://lookup.dbpedia.org/api/search/KeywordSearch?'
URL_DBPEDIA_SPOTLIGHT = 'http://localhost:2222/rest/annotate'


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

DOSSIER = ONT['Dossier']
ACTIVITY = ONT['Activity']
DOSSIER_TITLE = ONT['dossierTitle']
PROCESSED_BY = ONT['processedBy']
HAS_ACTIVITY = ONT['hasActivity']
REACHED_STAGE = ONT['reachedStage']
PROCEDURE_TYPE = ONT['procedureType']
GEO_AREA = ONT['geoArea']

START_DATE = ONT['startDate']
END_DATE = ONT['endDate']

HAS_TITLE = ONT['hasTitle']

HAS_DOC = ONT['hasDocument']

IS_RESPONSIBLE = ONT['isResponsibleIn']
IS_INVOLVED = ONT['isInvolvedIn']
HAS_RAPPORTEUR = ONT['hasRapporteur']

ABSTAINS = ONT['abstains']
VOTES_FOR = ONT['votesFor']
VOTES_AGAINST = ONT['votesAgainst']
VOTES_IN = ONT['votesIn']

HAS_TYPE = ONT['hasType']
HAS_BODY = ONT['hasBody']

PARTY = DBO['party']

REPRESENTS_COUNTRY = ONT['representsCountry']

IS_WITHIN = ONT['isWithin']
HAS_MEMBERSHIP = ONT['hasMembership']
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

GENDER = FOAF.gender
MALE = Literal('male', datatype=XSD.string)
FEMALE = Literal('female', datatype=XSD.string)
EUROPEAN_PARLIAMENT = DBR['European_Parliament']
EUROPEAN_COUNCIL = DBR['European_Council']
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

VOTES = {'Abstain': ABSTAINS, 'For': VOTES_FOR, 'Against': VOTES_AGAINST}
