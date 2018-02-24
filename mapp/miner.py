import re
from datetime import datetime
import urllib.parse as urlparse
from SPARQLEndpoint import SparqlServer
from packages.iribaker.iribaker import to_iri
from rdflib import URIRef, Literal
import logging
from timeit import default_timer as timer
from timing_handler import get_elapsed_seconds
import multiprocessing
from dataset_generator import DatasetGenerator
import json
import os
import spotlight

import io_handler as io
import constants as c
import formatting as fmt

# TODO () Look into addN() function for adding multiple triples in one go
# https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph.addN


class Miner(object):
    """Miner module."""

    def __init__(self, manager):
        # External URIs (DBPedia etc)
        self.mep_ext_uris = manager.dict()
        self.party_ext_uris = manager.dict()
        self.places_ext_uris = manager.dict()

        # Internal URIs
        self.dict_mep = manager.dict()
        self.dict_parties = manager.dict()
        self.dict_dossier = manager.dict()
        self.dict_committees = manager.dict()
        # self.dict_docs = manager.dict()

        self.list_activities = manager.list()
        self.list_procedures = manager.list()
        self.list_doc_types = manager.list()

        self.sparql_endpoint = SparqlServer(c.SPARQL_ENDPOINT)

        self.total_triples = 0

        logging.basicConfig(filename=c.MAIN_LOG,
                            level=logging.INFO,
                            format='[%(asctime)s] [%(levelname)s] %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p'
                            )

    def start(self, num_threads, mep_limit, dossier_limit, vote_limit):
        """Starts the miner class with the given configuration."""

        loaded_dict = io.load_json(c.EXTERNAL_MEP_URIS)
        if loaded_dict is not None:
            self.mep_ext_uris.update(loaded_dict)

        loaded_dict = io.load_json(c.EXTERNAL_PARTY_URIS)
        if loaded_dict is not None:
            self.party_ext_uris.update(loaded_dict)

        loaded_dict = io.load_json(c.EXTERNAL_PLACES_URIS)
        if loaded_dict is not None:
            self.places_ext_uris.update(loaded_dict)

        # TEMP
        loaded_dict = io.load_json(c.JSON_DIR + 'procedures.json')
        if loaded_dict is not None:
            self.list_procedures.extend(loaded_dict)

        loaded_dict = io.load_json(c.JSON_DIR + 'activities.json')
        if loaded_dict is not None:
            self.list_activities.extend(loaded_dict)

        loaded_dict = io.load_json(c.JSON_DIR + 'doc_types.json')
        if loaded_dict is not None:
            self.list_doc_types.extend(loaded_dict)

        results = self.convert_meps(c.DIR_MEPS, num_threads, mep_limit)
        if results:
            total_mep_triples, total_meps, time = results
            print(fmt.OK_SYMBOL, "Mined %i MEPs (%i triples). Took %f seconds\n" % (total_meps, total_mep_triples, time))
        else:
            return False

        io.save_dict_to_json(c.EXTERNAL_MEP_URIS, self.mep_ext_uris)
        io.save_dict_to_json(c.EXTERNAL_PARTY_URIS, self.party_ext_uris)

        results = self.convert_dossiers(c.DIR_DOSSIERS, num_threads, dossier_limit)
        if results:
            total_dossier_triples, total_dossiers, time = results
            print(fmt.OK_SYMBOL, "Mined %i dossiers (%i triples). Took %f seconds\n" % (total_dossiers, total_dossier_triples, time))
        else:
            return False

        io.save_dict_to_json(c.EXTERNAL_PLACES_URIS, self.places_ext_uris)

        io.save_list_to_json(c.JSON_DIR + 'activities.json', self.list_activities)
        io.save_list_to_json(c.JSON_DIR + 'procedures.json', self.list_procedures)
        io.save_list_to_json(c.JSON_DIR + 'doc_types.json', self.list_doc_types)

        results = self.convert_votes(c.DIR_VOTES, num_threads, vote_limit)
        if results:
            total_vote_triples, total_votes, time = results
            print(fmt.OK_SYMBOL, "Mined %i related votes (%i triples). Took %f seconds\n" % (total_votes, total_vote_triples, time))
        else:
            return False

        self.total_triples = total_mep_triples + total_dossier_triples + total_vote_triples
        # io.save_graph(c.GRAPH_OUTPUT, graph)
        # io.save_dataset(c.DATA_OUTPUT, miner.dataset)

    # def mepid_to_profile_iri(id):
    # return URIRef(to_iri('http://www.europarl.europa.eu/meps/en/' + str(id)
    # + '/_history.html'))

    @staticmethod
    def mep_to_lpv(id_):
        id_string = str(id_)

        return URIRef(to_iri(c.lp + 'EUmember_' + id_string))

    # Needs changing?
    @staticmethod
    def id_to_iri(id_, prefix=None):
        id_string = str(id_)
        if prefix:
            id_string = prefix + '_' + id_string

        return URIRef(to_iri(c.ont + id_string))

    @staticmethod
    def format_name_string(input_string):
        input_string = re.sub('\(.+?\)', '', input_string)
        input_string = input_string.lower().title().strip()
        input_string = re.sub('\s+', '_', input_string)
        return str(urlparse.quote_plus(input_string.replace('.', '_')))

    @staticmethod
    def get_dbpedia_lookup_uris(search_string, search_class=None, max_results=5):
        query = 'MaxHits=' + str(max_results) + '&QueryString=' + urlparse.quote_plus(search_string)
        if search_class:
            query += '&QueryClass=' + urlparse.quote_plus(search_class)

        resp = io.get_request(c.URL_DBPEDIA_LOOKUP + query)

        uris = []
        if resp:
            for result in resp['results']:
                uri = result['uri']
                if uri not in uris:
                    uris.append(uri)
        elif resp is False:
            return False

        return uris

    @staticmethod
    def get_dbpedia_spotlight_uris(search_string, filters):
        uris = []

        try:
            annotations = spotlight.annotate(c.URL_DBPEDIA_SPOTLIGHT, search_string, filters=filters)

            for result in annotations:
                uri = result['URI']
                if uri not in uris:
                    uris.append(uri)
        except spotlight.SpotlightException as e:
            pass

        return uris

    @staticmethod
    def fetch_uris_from_name(name, keywords='', search_class=None, max_results=5):
        uris = []
        dbpedia_uris = Miner.get_dbpedia_lookup_uris(name + ' ' + keywords, search_class=search_class, max_results=max_results)

        if dbpedia_uris:
            uris = dbpedia_uris
        elif dbpedia_uris is False:  # Failed, but uris might still be available, so don't generate one
            return uris
        else:  # Nothing found with spotlight, so just create a uri from the name string
            formatted = Miner.format_name_string(name)
            iri = to_iri(c.dbr + formatted)
            uris.append(iri)

        return uris

    def key_exists(self, key, uri_dict):
        key = str(key)
        if key in uri_dict:
            return True
        else:
            return False

    def uris_exist(self, key, uri_dict):
        key = str(key)
        if self.key_exists(key, uri_dict):  # Check if the key exists in the dictionary and has a list
            if uri_dict[key]:  # Check if the list is empty
                return True

        return False

    def add_uris(self, uris, key, uri_dict):
        key = str(key)
        if not self.key_exists(key, uri_dict):
            uri_dict[key] = []

        if type(uris) is not list:  # If it's a single uri (string), convert it to a list anyway
            uris = [uris]

        """
        for uri in uris:
            if uri not in uri_dict[key][selected_list]:
                uri_dict[key][selected_list].append(uri)
        """

        uri_dict[key] = uris

    def get_uris(self, key, uri_dict):
        key = str(key)
        if self.uris_exist(key, uri_dict):
            return uri_dict[key]
        else:
            return []

    def process_mep(self, index):
        triples = set()

        mep = io.load_json(os.path.join(c.DIR_MEPS, str(index) + '.json'), verbose=False)

        date_now = datetime.now().date()

        # Get raw values
        mep_id = int(mep['UserID'])
        # user_id = str(mep['_id'])
        full_name = Literal(str(mep['Name']['full'].lower().title().strip()), datatype=c.STRING)

        profile_url = Literal(str(mep['meta']['url']), datatype=c.URI)
        mep_uri = Miner.id_to_iri(mep_id, prefix='mep')

        # If no URIs exists, fetch any existing ones and add them to our dictionary
        if not self.uris_exist(mep_id, self.mep_ext_uris):
            mep_ext_uris = Miner.fetch_uris_from_name(full_name, keywords='politician', max_results=1)  # For some reason results are best without search_class='person'
            self.add_uris(mep_ext_uris, mep_id, self.mep_ext_uris)

        # Add all external URIs as the same induvidual
        for ext_uri in self.get_uris(mep_id, self.mep_ext_uris):
            triples.add((mep_uri, c.SAME_AS, URIRef(ext_uri)))

        # TODO: Make this more integrated
        triples.add((mep_uri, c.SAME_AS, Miner.mep_to_lpv(mep_id)))

        # append to temp dictionary of processed MEPs
        self.dict_mep[mep_id] = mep_uri

        if 'Photo' in mep:
            photo_url = Literal(str(mep['Photo']), datatype=c.IMAGE)
            triples.add((mep_uri, c.THUMBNAIL, photo_url))

        if 'Birth' in mep:
            if 'date' in mep['Birth']:
                birth_date = mep['Birth']['date']
                if birth_date != '':
                    birth_date = Literal(datetime.strptime(birth_date.split('T')[0], '%Y-%m-%d').date(), datatype=c.DATE)
                    triples.add((mep_uri, c.BIRTH_DATE, birth_date))

            if 'place' in mep['Birth']:
                birth_place = mep['Birth']['place'].strip().lower()

                # If no URIs exists, fetch any existing ones and add them to our dictionary
                if not self.uris_exist(birth_place, self.places_ext_uris):
                    birth_place_uris = Miner.fetch_uris_from_name(birth_place, search_class='place', max_results=5)
                    self.add_uris(birth_place_uris, birth_place, self.places_ext_uris)

                uris = self.get_uris(birth_place, self.places_ext_uris)
                if uris:
                    triples.add((mep_uri, c.BIRTH_PLACE, URIRef(uris[0])))

        if 'Death' in mep:
            death_date = str(mep['Death'])
            death_date = Literal(datetime.strptime(death_date.split('T')[0], '%Y-%m-%d').date(), datatype=c.DATE)
            triples.add((mep_uri, c.DEATH_DATE, death_date))

        # if 'active' in mep: active = mep['active'] # interesting but
        # unused atm

        # twitter = mep['Twitter']

        if 'Groups' in mep:
            for group in mep['Groups']:
                party_id = group['groupid']
                party_title = group['Organization']
                party_uri = self.id_to_iri(party_title)

                party_ids = set()
                if type(party_id) is list:
                    party_ids.update(party_id)
                    # TODO: Link older parties to their newer version with some instance inc date if possible
                    party_id = party_id[0]  # Select the latest as the main id TODO: Improve/Check this?
                else:
                    party_ids.add(party_id)

                # Map the ID to the internal URI
                if not self.key_exists(party_id, self.dict_parties):
                    self.dict_parties[party_id] = party_uri

                # Link external URIs to each party id that does not yet have some
                for id_ in party_ids:
                    if not self.uris_exist(id_, self.party_ext_uris):
                        party_ext_uris = Miner.fetch_uris_from_name(party_title, keywords='european union parliament', max_results=5)
                        self.add_uris(party_ext_uris, id_, self.party_ext_uris)

                # Link the internal party URI to all external counterparts
                for ext_uri in self.get_uris(party_id, self.party_ext_uris):
                    triples.add((party_uri, c.SAME_AS, URIRef(ext_uri)))

                start_date = datetime.strptime(group['start'].split('T')[0], '%Y-%m-%d').date()
                end_date = datetime.strptime(group['end'].split('T')[0], '%Y-%m-%d').date()

                membership_uri = self.id_to_iri(str(mep_id) + "_" + str(party_id) + "_" + str(start_date), prefix='membership')
                triples.add((membership_uri, c.START_DATE, Literal(start_date, datatype=c.DATE)))

                # If end date has passed
                if end_date <= date_now:
                    triples.add((membership_uri, c.END_DATE, Literal(end_date, datatype=c.DATE)))

                triples.add((mep_uri, c.HAS_MEMBERSHIP, membership_uri))
                triples.add((membership_uri, c.IS_WITHIN, party_uri))

                if 'country' in group:
                    country = group['country'].lower()

                    if not self.uris_exist(country, self.places_ext_uris):
                        country_ext_uris = Miner.fetch_uris_from_name(country, search_class='country', max_results=1)
                        self.add_uris(country_ext_uris, country, self.places_ext_uris)

                    ext_uris = self.get_uris(country, self.places_ext_uris)
                    if ext_uris:
                        triples.add((membership_uri, c.REPRESENTS_COUNTRY, URIRef(ext_uris[0])))

                if 'role' in group and group['role']:
                    role = str(group['role'])

                    if role in c.MEMBERSHIPS:
                        triples.add((membership_uri, c.TYPE, c.MEMBERSHIPS[role]))
                    else:
                        logging.error("Unknown role: %s", role)
                else:
                    logging.warning("No role found: MEP:%i start:%s party:%s. Adding as normal member.", mep_id, group['start'], party_title)
                    triples.add((membership_uri, c.TYPE, c.MEMBERSHIPS['Member']))

                triples.add((c.EUROPEAN_PARLIAMENT, c.IN_LEGISLATURE, party_uri))

        if 'Committees' in mep:
            for committee in mep['Committees']:
                committee_title = committee['Organization']
                # Since IDs are not always available, we use a formatted title string for now
                committee_id = self.format_name_string(committee_title)
                committee_uri = self.id_to_iri(committee_id)

                if not self.key_exists(committee_id, self.dict_committees):
                    self.dict_committees[committee_id] = committee_uri

                if 'role' in committee and committee['role']:
                    role = committee['role']

                    # start_date = group['start']
                    end_date = datetime.strptime(group['end'].split('T')[0], '%Y-%m-%d').date()

                    if role in c.MEMBERSHIPS:
                        triples.add((mep_uri, c.MEMBERSHIPS[role], URIRef(self.dict_committees[committee_id])))
                        # If end_date has passed
                        if end_date <= date_now:
                            pass  # TODO: add end date
                    else:
                        logging.error("Unknown role:", role)

        if 'Gender' in mep:
            gender = str(mep['Gender'])
            if gender == 'M':
                triples.add((mep_uri, c.GENDER, c.MALE))
            elif gender == 'F':
                triples.add((mep_uri, c.GENDER, c.FEMALE))
            else:
                logging.error("Unknown gender:", gender)
        else:
            logging.warning('No gender found: %s' % profile_url)

        """
        if 'Financial Declarations' in mep:
            declarations = mep['Financial Declarations']
            if declarations:
                print (json.dumps(declarations, indent=2))
        """

        triples.add((mep_uri, c.FULL_NAME, full_name))
        triples.add((mep_uri, c.URI, profile_url))
        triples.add((mep_uri, c.OFFICE, c.MEMBER_OF_EU))

        return triples

    def convert_meps(self, path, num_threads, limit):
        start = timer()
        counter = 0

        selected_meps = io.get_dataset_indexes(path, limit)

        print(fmt.WAIT_SYMBOL, "Mining MEPs...")

        try:
            pool = multiprocessing.Pool(num_threads)
            results = pool.map(self.process_mep, selected_meps)

            dataset = DatasetGenerator.get_dataset()
            for triples in results:
                for triple in triples:
                    dataset.add((triple[0], triple[1], triple[2]))

                counter += 1

                # Max 1000 MEPs per request
                if (counter % 1000) == 0 and counter != 0:
                    # reset dataset
                    if not self.sparql_endpoint.import_dataset(dataset):
                        return False

                    print(fmt.INFO_SYMBOL, counter, "MEPs imported.")
                    dataset = DatasetGenerator.get_dataset()

            # Import any left over from the last (incomplete) batch
            if not self.sparql_endpoint.import_dataset(dataset):
                    return False

            print(fmt.OK_SYMBOL, "Total of", counter, "MEPs imported.")

        finally:
            pool.close()
            pool.join()

        end = timer()

        return dataset.__len__(), counter, get_elapsed_seconds(start, end)

    def process_dossier(self, index):
        triples = set()

        dossier = io.load_json(os.path.join(c.DIR_DOSSIERS, str(index) + '.json'), verbose=False)

        dossier_id = dossier['_id']
        dossier_url = Literal(str(dossier['meta']['source']), datatype=c.URI)
        procedure = dossier['procedure']

        dossier_reference = procedure['reference']
        dossier_title = Literal(str(procedure['title'].strip()), datatype=c.STRING)
        # dossier_stage = Literal(str(procedure['stage_reached']), datatype=c.STRING)
        dossier_type = Literal(str(procedure['type']), datatype=c.STRING)

        # TEMP
        if procedure['type'] not in self.list_procedures:
            self.list_procedures.append(procedure['type'])

        dossier_uri = self.id_to_iri(dossier_reference, prefix='dossier')

        # Append to temp dictionary of dossiers processed
        self.dict_dossier[dossier_id] = dossier_uri

        # triples.add((dossier_uri, c.REACHED_STAGE, dossier_stage))
        triples.add((dossier_uri, c.PROCEDURE_TYPE, dossier_type))
        triples.add((dossier_uri, c.DOSSIER_TITLE, dossier_title))
        triples.add((dossier_uri, c.URI, dossier_url))

        if 'geographical_area' in procedure:
            if procedure['geographical_area']:
                geo_areas = [geo_area.lower() for geo_area in procedure['geographical_area']]
                for geo_area in geo_areas:
                    if not self.uris_exist(geo_area, self.places_ext_uris):
                        geo_ext_uris = Miner.fetch_uris_from_name(geo_area, search_class='place', max_results=5)
                        self.add_uris(geo_ext_uris, geo_area, self.places_ext_uris)

                    ext_uris = self.get_uris(geo_area, self.places_ext_uris)
                    if ext_uris:
                        triples.add((dossier_uri, c.GEO_AREA, URIRef(ext_uris[0])))

        for activity in dossier['activities']:
            # TODO: Filter out irelevant activities
            if 'type' in activity:
                if activity['type'] is not None:
                    activity_type = activity['type'].lower()
                    activity_id = dossier_id + '_' + activity_type
                    activity_uri = self.id_to_iri(activity_id, prefix='activity')
                    activity_date = Literal(datetime.strptime(activity['date'].split('T')[0], '%Y-%m-%d').date(), datatype=c.DATE)

                    # TEMP
                    if activity_type not in self.list_activities:
                        self.list_activities.append(activity_type)

                    triples.add((activity_uri, c.HAS_TYPE, Literal(activity_type, datatype=c.STRING)))
                    triples.add((activity_uri, c.DATE, activity_date))
                    triples.add((dossier_uri, c.HAS_ACTIVITY, activity_uri))

                    # if 'meeting_id' in activity:
                    #    if activity['meeting_id'] != None:
                    #        activity_id = int(activity['meeting_id'])

                    if 'body' in activity:
                        if activity['body']:
                            activity_body = str(activity['body'])
                            if activity_body is not 'unknown':  # TODO: Investigate why parltrack gives some as unknown
                                if activity_body in c.BODIES:
                                    bodies = c.BODIES[activity_body]

                                    for body in bodies:
                                        body_uri = body[c.PREFIX]

                                        triples.add((activity_uri, c.HAS_BODY, body_uri))
                                        triples.add((dossier_uri, c.PROCESSED_BY, body_uri))  # TODO: make this inferred?

                                        for ext_uri in body['dbpedia']:
                                            triples.add((body_uri, c.SAME_AS, ext_uri))  # TODO: check if this causes issues with duplicates
                                else:
                                    logging.error("Unknown activity body '%s'" % activity_body)

                    if 'title' in activity:
                        activity_title = Literal(str(activity['title']), datatype=c.STRING)
                        triples.add((activity_uri, c.HAS_TITLE, activity_title))

                    if 'docs' in activity:
                        for doc in activity['docs']:
                            # TODO: Filter out irelevant docs
                            doc_title = doc['title']
                            doc_id = activity_id + '_' + doc_title
                            doc_uri = self.id_to_iri(doc_id, prefix='document')

                            triples.add((activity_uri, c.HAS_DOC, doc_uri))
                            triples.add((doc_uri, c.HAS_TITLE, Literal(doc_title, datatype=c.STRING)))

                            if 'url' in doc:
                                if doc['url']:
                                    doc_url = Literal(str(doc['url']), datatype=c.URI)
                                    triples.add((doc_uri, c.URI, doc_url))

                            if 'type' in doc:
                                if doc['type']:
                                    doc_type = doc['type'].lower()
                                    triples.add((doc_uri, c.HAS_TYPE, Literal(doc_type, datatype=c.STRING)))

                                    # TODO: REMOVE
                                    if doc_type not in self.list_doc_types:
                                        self.list_doc_types.append(doc_type)
                else:
                    logging.warning("Activity has no type:", json.dumps(activity, indent=2))
            else:
                logging.warning("Activity has no type field!", json.dumps(activity, indent=2))

            for committee in dossier['committees']:
                committee_title = committee['committee_full']
                committee_id = self.format_name_string(committee_title)
                committee_uri = self.id_to_iri(committee_id)
                # committee_body = committee['body']
                committee_responsible = bool(committee['responsible'])

                if committee_responsible:
                    triples.add((committee_uri, c.IS_RESPONSIBLE, dossier_uri))
                else:
                    triples.add((committee_uri, c.IS_INVOLVED, dossier_uri))

                # TODO () Figure out ID troubles (ID doesn't match current
                # dictionary)
                """
                if 'rapporteur' in committee:
                    for rapporteur in committee['rapporteur']:
                        committee_rapporteur_id = str(rapporteur['mepref'])

                        if committee_rapporteur_id in self.mep_ext_uris:
                            mep_uri = URIRef(self.mep_ext_uris[committee_rapporteur_id][0])
                            triples.add([committee_uri, c.HAS_RAPPORTEUR , mep_uri])
                            print (mep_uri)
                        else:
                            print ("MEP not found:", committee_rapporteur_id)
                            print (json.dumps(rapporteur, indent=2), "\n")
                """

        return triples

    # TODO: See if there is a better dossier url to use instead of dossier['meta']['source']
    # TODO: See if there is a better dossier text to use instead of
    # dossier['procedure']['title']
    def convert_dossiers(self, path, num_threads, limit):
        start = timer()
        counter = 0
        num_triples = 0

        selected_dossiers = io.get_dataset_indexes(path, limit)

        print(fmt.WAIT_SYMBOL, "Mining Dossiers...")

        try:
            pool = multiprocessing.Pool(num_threads)
            results = pool.map(self.process_dossier, selected_dossiers)

            dataset = DatasetGenerator.get_dataset()
            for dossier in results:
                for triple in dossier:
                    dataset.add((triple[0], triple[1], triple[2]))

                num_triples += len(dossier)
                counter += 1

                # Max 1000 dossiers per request
                if (counter % 1000) == 0 and counter != 0:
                    # reset dataset
                    if not self.sparql_endpoint.import_dataset(dataset):
                        return False

                    print(fmt.INFO_SYMBOL, counter, "dossiers imported.")
                    dataset = DatasetGenerator.get_dataset()

            # Import any left over from the last (incomplete) batch
            if not self.sparql_endpoint.import_dataset(dataset):
                    return False

            print(fmt.OK_SYMBOL, "Total of", counter, "dossiers imported.")

        finally:
            pool.close()
            pool.join()

        end = timer()
        return num_triples, counter, get_elapsed_seconds(start, end)

    def process_votes(self, index):
        count = 0
        failed = 0
        triples = set()

        votes = io.load_json(os.path.join(c.DIR_VOTES, str(index) + '.json'), verbose=False)

        if 'epref' in votes:
            dossier_reference = votes['epref']
            if '_id' in votes:
                vote_id = votes['_id']
                vote_uri = self.id_to_iri(dossier_reference + '_' + vote_id, prefix='parlvote')

                if 'title' in votes:
                    vote_title = votes['title']
                    triples.add((URIRef(vote_uri), c.HAS_TITLE, Literal(vote_title, datatype=c.STRING)))

                if 'report' in votes:
                    report_id = str(votes['report'])
                    report_uri = self.id_to_iri(report_id, prefix='document')  # TODO: Make a dict and lookup from there?
                    triples.add((URIRef(vote_uri), c.BASED_ON_REPORT, report_uri))

                # If there's a dossier id and we processed this dossier, link the voting to the looked up URI, otherwise attempt to construct the URI and hope for the best
                if 'dossierid' in votes and self.key_exists(str(votes['dossierid']), self.dict_dossier):
                    dossier_uri = self.dict_dossier[str(votes['dossierid'])]
                else:
                    dossier_uri = self.id_to_iri(dossier_reference, prefix='dossier')

                triples.add((URIRef(vote_uri), c.IS_VOTE_FOR, URIRef(dossier_uri)))

                if 'url' in votes:
                    vote_url = votes['url']
                    triples.add((URIRef(vote_uri), c.URI, Literal(vote_url, datatype=c.URI)))

                # title = votes['title']
                # url = dossier['url']
                # ep_title = dossier['eptitle']

                for vote_type in c.VOTES:
                    if vote_type in votes:
                        for group in votes[vote_type]['groups']:
                            # group_name = group['group']
                            for vote in group['votes']:
                                try:
                                    if 'ep_id' in vote:
                                        voter_id = vote['ep_id']
                                    else:
                                        if 'name' in vote:
                                            logging.warning("MEP of vote had no epid. Do they exist? (%s). Attempting to use internal ID", vote['name'])
                                        voter_id = vote['userid']
                                except Exception as ex:
                                    logging.error("Skipping vote of type " + vote_type + " on dossier " + dossier_uri + " No ID found.")
                                    failed += 1
                                    continue

                                if self.key_exists(voter_id, self.dict_mep):
                                    voter_uri = URIRef(self.dict_mep[voter_id])
                                else:
                                    voter_uri = self.id_to_iri(voter_id, prefix='mep')

                                triples.add((voter_uri, c.VOTES[vote_type], vote_uri))
                                count += 1
            else:
                logging.warning("Votes has no id. Skipping.")
        else:
            logging.warning("No dossier reference (epref) found in votes. Skipping.")

        return count, failed, triples

    def convert_votes(self, path, num_threads, limit):
        start = timer()
        total_success = 0
        total_failed = 0
        num_triples = 0
        counter = 0

        selected_votes = io.get_dataset_indexes(path, limit)

        print(fmt.WAIT_SYMBOL, 'Mining votes...')

        try:
            pool = multiprocessing.Pool(num_threads)

            results = pool.map(self.process_votes, selected_votes)

            dataset = DatasetGenerator.get_dataset()
            for result in results:
                count, failed, triples = result
                total_failed += failed
                total_success += count
                num_triples += len(triples)

                counter += 1

                for triple in triples:
                    dataset.add((triple[0], triple[1], triple[2]))

                if (counter % 1000) == 0 and counter != 0:
                    # reset dataset
                    if not self.sparql_endpoint.import_dataset(dataset):
                        return False

                    print(fmt.INFO_SYMBOL, total_success, "votes imported.")
                    dataset = DatasetGenerator.get_dataset()

            # Import any left over from the last (incomplete) batch
            if not self.sparql_endpoint.import_dataset(dataset):
                return False

            print(fmt.OK_SYMBOL, "Total of", total_success, "votes imported.")

            if total_failed > 0:
                print(fmt.WARNING, '%i out of %i votes had no MEP ID and have been excluded.' % (total_failed, total_success + total_failed))

        finally:
            pool.close()
            pool.join()

        end = timer()

        return num_triples, total_success, get_elapsed_seconds(start, end)
