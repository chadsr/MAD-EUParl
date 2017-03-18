from rdflib import Namespace, XSD
import os

DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

LOG_DIR = DIR + '/logs/'
DATA_DIR = DIR + '/data/'

MAIN_LOG = LOG_DIR + 'parlialytics.log'

JSON_DIR = DATA_DIR + 'json/'
LD_DIR = DATA_DIR + 'linked_data/'

DATA_OUTPUT = LD_DIR + 'parlialytics.ttl'
GRAPH_OUTPUT = LD_DIR + 'parltrack-graph.ttl'

DATA_MEP = JSON_DIR + 'ep_meps_current.json'
DATA_VOTES = JSON_DIR + 'ep_votes.json'
DATA_DOSSIER = JSON_DIR + 'ep_dossiers.json'
DICT_MEPS = JSON_DIR + 'dict_meps.json'
DICT_PARTIES = JSON_DIR + 'dict_parties.json'
DICT_COMMITTEES = JSON_DIR + 'dict_committees.json'
DICT_MISC_VOTES = JSON_DIR + 'misc_votes.json'

SERVER_START = 'cd $STARDOG_HOME/bin && ./stardog-admin server start --disable-security'
SERVER_IMPORT_ONT = 'cd $STARDOG_HOME/bin && ./stardog-admin db create -o reasoning.type=DL reasoning.sameas=FULL -n parlialytics "' + \
    LD_DIR + 'parlialytics.ttl"'
SPARQL_ENDPOINT = 'http://localhost:5820/parlialytics/query'

DOWNLOAD_TIMEOUT = 30
DATA_URLS = ['http://parltrack.euwiki.org/dumps/ep_votes.json.xz',
             'http://parltrack.euwiki.org/dumps/ep_meps_current.json.xz',
             'http://parltrack.euwiki.org/dumps/ep_dossiers.json.xz']

DATABASE = 'http://localhost:5820/databases/parlialytics#'  # Database endpoint
NAMESPACE = DATABASE

ont = NAMESPACE
ONT = Namespace(ont)
PREFIX = 'epv'

# DOSSIER_TYPE = 'Legislative proposal published'

# eo = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
# GEO = Namespace(geo)

dbo = 'http://dbpedia.org/ontology/'
DBO = Namespace(dbo)
dbr = 'http://dbpedia.org/resource/'
DBR = Namespace(dbr)
dbp = 'http://dbpedia.org/property/'
DBP = Namespace(dbp)

rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDF = Namespace(rdf)

foaf = 'http://xmlns.com/foaf/0.1/'
FOAF = Namespace(foaf)

DOSSIER = ONT['Dossier']
ACTIVITY = ONT['Activity']
DOSSIER_TITLE = ONT['dossierTitle']
PROCESSED_BY = ONT['processedBy']
HAS_ACTIVITY = ONT['hasActivity']
REACHED_STAGE = ONT['reachedStage']
PROCEDURE_TYPE = ONT['procedureType']
GEO_AREA = ONT['geoArea']

IS_ACTIVE = ONT['isActive']

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
BUREAU_CHAIR = ONT['ChairOfTheBureau']
CHAIR = ONT['Chair']
PRESIDENT = ONT['President']
TREASURER = ONT['Treasurer']
BUREAU_MEMBER = ONT['MemberOfTheBureau']

GENDER = DBO['gender']
MALE = DBR['Male']
FEMALE = DBR['Female']
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

FULL_NAME = FOAF['name']
BIRTH_DATE = DBO['birthDate']
BIRTH_PLACE = DBO['birthPlace']
DEATH_DATE = DBO['deathDate']

URI = XSD['anyURI']
STRING = XSD['string']
DATE = XSD['date']
BOOLEAN = XSD.boolean

TYPE = RDF['type']
