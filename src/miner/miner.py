import re
from collections import defaultdict
from datetime import datetime
from itertools import islice
import urllib.parse as urlparse
import ijson

from SPARQLEndpoint import SparqlServer

from packages.iribaker.iribaker import to_iri
from rdflib import URIRef, Literal
import io_handler as io
import constants as c
import formatting as fmt

import logging

from timeit import default_timer as timer
from timing_handler import get_elapsed_seconds

from multiprocessing import Pool
from multiprocessing.managers import BaseManager, DictProxy
from dataset_generator import DatasetGenerator

# TODO () Look into addN() function for adding multiple triples in one go
# https://rdflib.readthedocs.io/en/stable/_modules/rdflib/graph.html#ConjunctiveGraph.addN


class DictManager(BaseManager):
    pass


DictManager.register('defaultdict', defaultdict, DictProxy)


class Miner(object):
    """Miner module."""

    def __init__(self):
        self.manager = DictManager()
        self.manager.start()

        # These are currently dict(lists), because there is a possibility of
        # multiple iris per key in the future
        """
        self.dict_mep = defaultdict(list)
        self.dict_party = defaultdict(list)
        self.dict_dossier = defaultdict(list)
        self.dict_committees = defaultdict(list)
        """

        self.dict_mep = self.manager.defaultdict(list)
        self.dict_party = self.manager.defaultdict(list)
        self.dict_dossier = self.manager.defaultdict(list)
        self.dict_committees = self.manager.defaultdict(list)

        self.sparql_endpoint = SparqlServer(c.SPARQL_ENDPOINT)

        json_str = io.load_json(c.DICT_MEPS)
        if json_str is not None:
            self.dict_mep = io.json_to_defaultdict(json_str)

        json_str = io.load_json(c.DICT_PARTIES)
        if json_str is not None:
            self.dict_party = io.json_to_defaultdict(json_str)

        self.total_triples = 0

        logging.basicConfig(filename=c.MAIN_LOG,
                            level=logging.INFO,
                            format='[%(asctime)s] [%(levelname)s] %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p'
                            )

    def start(self, num_threads, mep_limit, dossier_limit, vote_limit):
        """Starts the miner class with the given configuration."""

        results = self.convert_meps(c.DATA_MEP, num_threads, mep_limit)
        if results:
            mep_triples, count, time = results
            print(fmt.OK_SYMBOL, "Mined", count, "MEPs (" +
                  str(mep_triples), "triples). Took ", time, "seconds\n")
        else:
            return False

        io.save_dict_to_json(c.DICT_MEPS, self.dict_mep)
        io.save_dict_to_json(c.DICT_PARTIES, self.dict_party)

        results = self.convert_dossiers(c.DATA_DOSSIER, num_threads, dossier_limit)
        if results:
            dossier_triples, count, time = results
            print(fmt.OK_SYMBOL, "Mined", count, "dossiers (" +
                  str(dossier_triples), "triples). Took ", time, "seconds\n")
        else:
            return False

        results = self.convert_votes(c.DATA_VOTES, num_threads, vote_limit)
        if results:
            vote_triples, count, fails, time = results
            print(fmt.OK_SYMBOL, "Mined", count,
                  "related votes (" + str(vote_triples), "triples)", fails,
                  "votes failed to be parsed (No MEP ID). Took ", time, "seconds\n"
                  )
        else:
            return False

        self.total_triples = mep_triples + dossier_triples + vote_triples
        # io.save_graph(c.GRAPH_OUTPUT, graph)
        # io.save_dataset(c.DATA_OUTPUT, miner.dataset)

    # def mepid_to_profile_iri(id):
    # return URIRef(to_iri('http://www.europarl.europa.eu/meps/en/' + str(id)
    # + '/_history.html'))

    # Needs changing?
    @staticmethod
    def id_to_iri(id_):
        return URIRef(to_iri(c.ont + str(id_)))

    @staticmethod
    def format_name_string(input_string):
        input_string = re.sub('\(.+?\)', '', input_string)
        input_string = input_string.lower().title().strip()
        input_string = re.sub('\s+', '_', input_string)
        return str(urlparse.quote(input_string.replace('.', '_')))

    @staticmethod
    def name_to_dbr(name):
        formatted = Miner.format_name_string(name)
        iri = to_iri(c.dbr + formatted)
        # uriref = URIRef(iri)
        return iri

    def process_mep(self, mep):
        triples = []

        date_now = datetime.now().date()

        # Get raw values
        mep_id = int(mep['UserID'])
        # user_id = str(mep['_id'])
        full_name = Literal(
            str(mep['Name']['full'].lower().title().strip()),
            datatype=c.STRING
        )

        profile_url = Literal(str(mep['meta']['url']), datatype=c.URI)
        mep_uri = self.name_to_dbr(full_name)

        mep_uri = URIRef(mep_uri)

        if 'Photo' in mep:
            photo_url = Literal(str(mep['Photo']), datatype=c.IMAGE)
            triples.append((mep_uri, c.THUMBNAIL, photo_url))

        if 'Birth' in mep:
            if 'date' in mep['Birth']:
                birth_date = mep['Birth']['date']
                if birth_date != '':
                    birth_date = Literal(
                        datetime.strptime(
                            birth_date.split('T')[0], '%Y-%m-%d'
                        ).date(),
                        datatype=c.DATE
                    )

                    triples.append((mep_uri, c.BIRTH_DATE, birth_date))

            if 'place' in mep['Birth']:
                birth_place = URIRef(self.name_to_dbr(
                    str(mep['Birth']['place'].strip())))

                triples.append((mep_uri, c.BIRTH_PLACE, birth_place))

        if 'Death' in mep:
            death_date = str(mep['Death'])
            death_date = Literal(datetime.strptime(death_date.split('T')[
                                 0], '%Y-%m-%d').date(), datatype=c.DATE)

            triples.append((mep_uri, c.DEATH_DATE, death_date))

        # if 'active' in mep: active = mep['active'] # interesting but
        # unused atm

        # twitter = mep['Twitter']

        if 'Groups' in mep:
            for group in mep['Groups']:
                party_id = group['groupid']
                party_title = str(group['Organization'])
                party_dbr = self.name_to_dbr(party_title)

                if type(party_id) is list:
                    for pid in party_id:
                        if party_dbr not in self.dict_party[pid]:
                            self.dict_party[pid].append(party_dbr)
                    party_id = party_id[0]
                elif party_dbr not in self.dict_party[party_id]:
                    self.dict_party[party_id].append(party_dbr)

                start_date = datetime.strptime(
                    group['start'].split('T')[0], '%Y-%m-%d').date()
                end_date = datetime.strptime(
                    group['end'].split('T')[0], '%Y-%m-%d').date()

                # If a valid iri was added manually, it's always first, so
                # just take the first
                party_uri = URIRef(str(self.dict_party[party_id][0]))

                membership_uri = self.id_to_iri(
                    full_name + "_" + party_id + "_" + str(start_date))

                triples.append((membership_uri, c.START_DATE, Literal(start_date, datatype=c.DATE)))

                # If end date has passed
                if end_date <= date_now:
                    triples.append((membership_uri, c.END_DATE, Literal(end_date, datatype=c.DATE)))

                triples.append((mep_uri, c.HAS_MEMBERSHIP, membership_uri))
                triples.append((membership_uri, c.IS_WITHIN, party_uri))

                if 'country' in group:
                    country = group['country']
                    country_dbr = URIRef(self.name_to_dbr(country))
                    triples.append(
                        (membership_uri, c.REPRESENTS_COUNTRY, country_dbr)
                    )

                if 'role' in group and group['role']:
                    role = str(group['role'])

                    if role in c.MEMBERSHIPS:
                        triples.append(
                            (membership_uri, c.TYPE, c.MEMBERSHIPS[role])
                        )
                    else:
                        logging.warning("Unknown role: %s", role)
                else:
                    logging.warning("No role found: %s %s %s",
                                    profile_url, group['start'], party_title)

                triples.append(
                    (c.EUROPEAN_PARLIAMENT, c.IN_LEGISLATURE, party_uri))

        """
        if 'Committees' in mep:
            mep_committees = []

            for committee in mep['Committees']:
                committee_title = committee['Organization']
                # Since IDs are not always available, we use a formatted title string for now
                committee_id = self.format_name_string(committee_title)
                committee_uri = self.id_to_iri(committee_id)

                if committee_uri not in self.dict_committees[committee_id]:
                    self.dict_committees[committee_id].append(committee_uri)

                if 'role' in committee:
                    role = str(committee['role'])

                    if role != "":
                        if committee_id not in mep_committees:
                            mep_committees.append(committee_id)
                            #start_date = group['start']
                            end_date = datetime.strptime(group['end'].split('T')[0], '%Y-%m-%d').date()

                            if role in role_dict:
                                # If end_date has passed
                                if end_date <= date_now:
                                    triples.append((mep_uri, role_dict[role][1], committee_uri))
                                else:
                                    triples.append((mep_uri, role_dict[role][0], committee_uri))
                            else:
                                print ("Unknown role:", role)
        """
        if 'Gender' in mep:
            gender = str(mep['Gender'])
            if gender == 'M':
                triples.append((mep_uri, c.GENDER, c.MALE))
            elif gender == 'F':
                triples.append((mep_uri, c.GENDER, c.FEMALE))
            else:
                print("Unknown gender:", gender)
        else:
            logging.warning('No gender found: %s', profile_url)

        """
        if 'Financial Declarations' in mep:
            declarations = mep['Financial Declarations']
            if declarations:
                print (json.dumps(declarations, indent=2))
        """

        triples.append((mep_uri, c.FULL_NAME, full_name))
        triples.append((mep_uri, c.URI, profile_url))
        triples.append((mep_uri, c.OFFICE, c.MEMBER_OF_EU))

        return [mep_id, mep_uri, triples]

    def convert_meps(self, path, num_threads, limit):
        start = timer()
        counter = 0
        input_dict = self.manager.defaultdict(list)

        print(fmt.WAIT_SYMBOL, "Getting relevant dataset...")

        with open(path) as f:
            objects = ijson.items(f, 'item')
            objects = islice(objects, limit)

            for i, obj in enumerate(objects):
                input_dict[i] = obj

        f.close()

        print(fmt.WAIT_SYMBOL, "Mining MEPs...")

        try:
            pool = Pool(num_threads)
            results = pool.map(self.process_mep, input_dict)

            dataset = DatasetGenerator.get_dataset()
            for mep in results:
                # append to global dictionary
                if not self.dict_mep[mep[0]].append(mep[1]):
                    self.dict_mep[mep[0]].append(mep[1])

                for triple in mep[2]:
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

    def process_dossier(self, dossier):
        triples = []

        dossier_id = dossier['_id']
        dossier_url = Literal(str(dossier['meta']['source']), datatype=c.URI)

        procedure = dossier['procedure']

        dossier_title = Literal(
            str(procedure['title'].strip()), datatype=c.STRING)
        dossier_stage = Literal(
            str(procedure['stage_reached']), datatype=c.STRING)
        # dossier_type = Literal(str(procedure['type']), datatype=c.STRING)

        dossier_uri = URIRef(self.name_to_dbr(dossier_title))

        try:
            triples.append([dossier_uri, c.REACHED_STAGE, dossier_stage])
            # triples.append([dossier_uri, c.PROCEDURE_TYPE, dossier_title])
            triples.append([dossier_uri, c.DOSSIER_TITLE, dossier_title])
            triples.append([dossier_uri, c.URI, dossier_url])
            triples.append(
                [dossier_uri, c.PROCESSED_BY, c.EUROPEAN_PARLIAMENT])

            # dataset.add((dossier_uri, RDF.type, DOSSIER))

            if 'geographical_area' in procedure:
                if procedure['geographical_area']:
                    geo_areas = procedure['geographical_area']
                    for geo_area in geo_areas:
                        dossier_geo = URIRef(self.name_to_dbr(geo_area))
                        triples.append([dossier_uri, c.GEO_AREA, dossier_geo])

            for activity in dossier['activities']:
                if 'type' in activity:
                    if activity['type'] is not None:
                        activity_id = dossier_title + '#' + activity['type']
                        activity_uri = URIRef(self.name_to_dbr(activity_id))
                        activity_type = Literal(
                            str(activity['type']), datatype=c.STRING)
                        activity_date = Literal(
                            datetime.strptime(activity['date'].split('T')[
                                              0], '%Y-%m-%d').date(),
                            datatype=c.DATE)

                        triples.append(
                            [activity_uri, c.HAS_TYPE, activity_type])
                        triples.append([activity_uri, c.DATE, activity_date])
                        triples.append(
                            [dossier_uri, c.HAS_ACTIVITY, activity_uri])

                        # if 'meeting_id' in activity:
                        #    if activity['meeting_id'] != None:
                        #        activity_id = int(activity['meeting_id'])

                        if 'body' in activity:
                            if activity['body'] is not None:
                                activity_body = str(activity['body'])
                                if activity_body == "EP":
                                    triples.append(
                                        [
                                            activity_uri,
                                            c.HAS_BODY,
                                            c.EUROPEAN_PARLIAMENT
                                        ])
                                elif activity_body == "EC":
                                    triples.append(
                                        [
                                            activity_uri,
                                            c.HAS_BODY,
                                            c.EUROPEAN_COUNCIL
                                        ])
                                # else:
                                #    print ("Unknown activity body:", activity_body)

                        if 'title' in activity:
                            activity_title = Literal(
                                str(activity['title']), datatype=c.STRING)
                            triples.append(
                                [activity_uri, c.HAS_TITLE, activity_title])

                        if 'docs' in activity:
                            for doc in activity['docs']:
                                doc_title = Literal(
                                    str(doc['title']), datatype=c.STRING)
                                doc_uri = URIRef(self.name_to_dbr(
                                    activity_id + '#' + doc_title))

                                triples.append(
                                    [activity_uri, c.HAS_DOC, doc_uri])
                                triples.append(
                                    [doc_uri, c.HAS_TITLE, doc_title])

                                if 'url' in doc:
                                    if doc['url']:
                                        doc_url = Literal(
                                            str(doc['url']), datatype=c.URI)
                                        triples.append(
                                            [doc_uri, c.URI, doc_url])

                                if 'type' in doc:
                                    if doc['type']:
                                        doc_type = Literal(
                                            str(doc['type']),
                                            datatype=c.STRING
                                        )

                                        triples.append(
                                            [doc_uri, c.HAS_TYPE, doc_type])
                    else:
                        print("Activity type is none!")
                else:
                    print("Activity has not type field!")

                for committee in dossier['committees']:
                    committee_title = committee['committee_full']
                    committee_id = self.format_name_string(committee_title)
                    committee_uri = self.id_to_iri(committee_id)
                    # committee_body = committee['body']
                    committee_responsible = bool(committee['responsible'])

                    if committee_responsible:
                        triples.append(
                            [committee_uri, c.IS_RESPONSIBLE, dossier_uri])
                    else:
                        triples.append(
                            [committee_uri, c.IS_INVOLVED, dossier_uri])

                    # TODO () Figure out ID troubles (ID doesn't match current
                    # dictionary)
                    """
                    if 'rapporteur' in committee:
                        for rapporteur in committee['rapporteur']:
                            committee_rapporteur_id = str(rapporteur['mepref'])

                            if committee_rapporteur_id in self.dict_mep:
                                mep_uri = URIRef(self.dict_mep[committee_rapporteur_id][0])
                                triples.append([committee_uri, c.HAS_RAPPORTEUR , mep_uri])
                                print (mep_uri)
                            else:
                                print ("MEP not found:", committee_rapporteur_id)
                                print (json.dumps(rapporteur, indent=2), "\n")
                    """

        except Exception as ex:
            print("Exception:", ex)

        return [dossier_id, dossier_uri, triples]

    # TODO: See if there is a better dossier url to use instead of dossier['meta']['source']
    # TODO: See if there is a better dossier text to use instead of
    # dossier['procedure']['title']
    def convert_dossiers(self, path, num_threads, limit):
        start = timer()
        counter = 0
        num_triples = 0

        input_dict = self.manager.defaultdict(list)

        print(fmt.WAIT_SYMBOL, "Getting relevant dataset...")

        with open(path) as f:
            objects = ijson.items(f, 'item')
            objects = islice(objects, limit)

            for i, obj in enumerate(objects):
                input_dict[i] = obj

        f.close()

        print(fmt.WAIT_SYMBOL, "Mining Dossiers...")

        try:
            pool = Pool(num_threads)
            results = pool.map(self.process_dossier, input_dict)

            dataset = DatasetGenerator.get_dataset()
            for dossier in results:
                self.dict_dossier[dossier[0]].append(dossier[1])

                for triple in dossier[2]:
                    dataset.add((triple[0], triple[1], triple[2]))

                num_triples += len(dossier[2])
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

    def process_votes(self, votes):
        counter = 0
        failed = 0
        triples = []

        if 'dossierid' in votes:
            dossier_id = votes['dossierid']

            # If this dossier is in our dictionary of useful dossiers, continue
            if dossier_id in self.dict_dossier:
                dossier_uri = URIRef(self.dict_dossier[dossier_id][0])
                # title = votes['title']
                # url = dossier['url']
                # ep_title = dossier['eptitle']

                for vote_type in c.VOTES:
                    if vote_type in votes:
                        for group in votes[vote_type]['groups']:
                            # group_name = group['group']
                            for vote in group['votes']:
                                try:
                                    voter_id = int(vote['ep_id'])
                                    # voter_id = str(vote['id'])
                                except Exception as ex:
                                    # logging.error("Skipping vote of type "+vote_type+" on dossier "+dossier_uri+" Invalid MEP id.")
                                    failed += 1
                                    continue

                                if voter_id in self.dict_mep:
                                    voter_uri = URIRef(
                                        self.dict_mep[voter_id][0])
                                    try:
                                        triples.append(
                                            [
                                                voter_uri,
                                                c.VOTES[vote_type],
                                                dossier_uri
                                            ])
                                    except Exception as ex:
                                        print(ex)
                                        continue
                                else:
                                    logging.warning("MEP not found. Using their ID instead. (%i)", voter_id)

                                    try:
                                        triples.append(
                                            [
                                                c.MEMBER_OF_EU,
                                                c.VOTES[vote_type],
                                                dossier_uri
                                            ])
                                    except Exception as ex:
                                        print(ex)
                                        continue
                                counter += 1

        return [counter, failed, triples]

    def convert_votes(self, path, num_threads, limit):
        start = timer()
        counter = 0
        failed = 0
        num_triples = 0
        input_dict = self.manager.defaultdict(list)

        print(fmt.WAIT_SYMBOL, "Getting relevant dataset...")

        with open(path) as f:
            objects = ijson.items(f, 'item')
            objects = islice(objects, limit)

            for i, obj in enumerate(objects):
                input_dict[i] = obj

        f.close()

        print(fmt.WAIT_SYMBOL, 'Mining votes...')

        try:
            pool = Pool(num_threads)

            results = pool.map(self.process_votes, input_dict)

            dataset = DatasetGenerator.get_dataset()
            for result in results:
                failed += result[1]

                for triple in result[2]:
                    if triple[0] is not None:
                        dataset.add((triple[0], triple[1], triple[2]))
                    else:
                        print(triple)

                counter += result[0]
                num_triples += len(result[2])

                if (counter % 1000) == 0 and counter != 0:
                    # reset dataset
                    if not self.sparql_endpoint.import_dataset(dataset):
                        return False

                    print(fmt.INFO_SYMBOL, counter, "votes imported.")
                    dataset = DatasetGenerator.get_dataset()

            # Import any left over from the last (incomplete) batch
            if not self.sparql_endpoint.import_dataset(dataset):
                return False

            print(fmt.OK_SYMBOL, "Total of", counter, "votes imported.")

            if failed > 0:
                logging.warning('%s out of %s had no MEP ID',
                                str(failed), str(counter))

        finally:
            pool.close()
            pool.join()

        end = timer()
        return num_triples, counter, failed, get_elapsed_seconds(start, end)
