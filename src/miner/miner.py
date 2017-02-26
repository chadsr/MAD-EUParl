import re
from collections import defaultdict
from datetime import datetime
from itertools import islice
import json
import urllib.parse as urlparse

from packages.iribaker.iribaker import to_iri
from rdflib import URIRef, Literal

import io_handler as io
import constants as c
import formatting as fmt

from timeit import default_timer as timer
from timing import get_elapsed_seconds

from multiprocessing import Pool
from dataset_generator import DatasetGenerator

class Miner(object):
    def __init__(self):
        # These are currently dict(lists), because there is a possibility of multiple iris per key in the future
        self.dict_mep = defaultdict(list)
        self.dict_party = defaultdict(list)
        self.dict_dossier = defaultdict(list)

        json_str = io.load_json(c.DICT_MEPS)
        if json_str is not None:
            self.dict_mep = io.json_to_defaultdict(json_str)

        json_str = io.load_json(c.DICT_PARTIES)
        if json_str is not None:
            self.dict_party = io.json_to_defaultdict(json_str)

        self.dataset = DatasetGenerator.get_dataset()

    def start(self, num_threads):
        print (fmt.WAIT_SYMBOL, "Mining MEPS...")
        count, time = self.convert_meps(c.DATA_MEP)

        io.save_json(c.DICT_MEPS, self.dict_mep)
        io.save_json(c.DICT_PARTIES, self.dict_party)

        print (fmt.WAIT_SYMBOL, "Mining dossiers...")
        count, time = self.convert_dossier(c.DATA_DOSSIER)
        print (fmt.OK_SYMBOL, "Mined", count, "dossiers. Took ", time, "seconds")

        print (fmt.WAIT_SYMBOL, 'Mining votes...')
        count, time = self.convert_votes(c.DATA_VOTES, num_threads)
        print (fmt.OK_SYMBOL, "Mined", count, "related votes. Took ", time, "seconds")

    # def mepid_to_profile_iri(id):
    #   return URIRef(to_iri('http://www.europarl.europa.eu/meps/en/' + str(id) + '/_history.html'))

    # Needs changing?
    @staticmethod
    def id_to_iri(id_):
        return URIRef(to_iri(c.ont + str(id_)))

    @staticmethod
    def format_name_string(input_string):
        input_string = re.sub('\(.+?\)', '', input_string)
        input_string = input_string.lower().title().strip()
        input_string = re.sub('\s+', '_', input_string)
        return str(urlparse.quote(input_string.replace('.','_')))

    @staticmethod
    def name_to_dbr(name):
        formatted = Miner.format_name_string(name)
        iri = to_iri(c.dbr + formatted)
        #uriref = URIRef(iri)
        return iri

    # TODO: See if there is a better dossier url to use instead of dossier['meta']['source']
    # TODO: See if there is a better dossier text to use instead of dossier['procedure']['title']
    def convert_dossier(self, path):
        json_data = io.load_json(path)
        counter = 0

        start = timer()
        for dossier in islice(json_data, 0, c.DOSSIER_LIMIT):
            for activity in dossier['activities']:
                if 'type' in activity:
                    if activity['type'] != None:
                        dossier_activity = Literal(str(activity['type']), datatype=c.STRING)
                    #if activity['type'] == c.DOSSIER_TYPE:
                        dossier_id = dossier['_id']
                        dossier_url = Literal(str(dossier['meta']['source']), datatype=c.URI)
                        dossier_date = Literal(
                            datetime.strptime(dossier['activities'][0]['date'].split('T')[0], '%Y-%m-%d').date(),
                            datatype=c.DATE)
                        dossier_title = Literal(str(dossier['procedure']['title'].strip()), datatype=c.STRING)

                        # User the meta url as the iri
                        dossier_uri = URIRef(to_iri(dossier_url))

                        self.dataset.add((dossier_uri, c.PROCESSED_BY, c.EUROPEAN_PARLIAMENT))
                        # dataset.add((dossier_uri, RDF.type, DOSSIER))
                        self.dataset.add((dossier_uri, c.DOSSIER_TITLE, dossier_title))
                        self.dataset.add((dossier_uri, c.URI, dossier_url))
                        self.dataset.add((dossier_uri, c.DATE, dossier_date))
                        self.dataset.add((dossier_uri, c.ACTIVITY_TYPE, dossier_activity))

                        # Store the id and uri in the dictionary for use later
                        self.dict_dossier[dossier_id].append(dossier_uri)

                        #print ('Dossier:', dossier_uri)
                        counter += 1
                        break  # dossier matches DOSSIER_TYPE, no need to search more activities

        end = timer()
        return counter, get_elapsed_seconds(start, end)

    def process_votes(self, votes):
        vote_dict = {'Abstain':c.ABSTAINS, 'For':c.VOTES_FOR, 'Against':c.VOTES_AGAINST}
        counter = 0

        if 'dossierid' in votes:
            dossier_id = votes['dossierid']

            # If this dossier is in our dictionary of useful dossiers, continue
            if dossier_id in self.dict_dossier:
                dossier_uri = self.dict_dossier[dossier_id][0]
                # title = votes['title']
                # url = dossier['url']
                # ep_title = dossier['eptitle']

                for vote_type in vote_dict:
                    if vote_type in votes:
                        for group in votes[vote_type]['groups']:
                            # group_name = group['group']
                            for vote in group['votes']:
                                # user_id = vote['userid']
                                voter_id = str(vote['ep_id'])
                                if voter_id in self.dict_mep:
                                    self.dataset.add((URIRef(str(self.dict_mep[voter_id][0])), vote_dict[vote_type], dossier_uri))
                                    counter += 1
        return counter

    def convert_votes(self, path, num_threads):
        json_data = io.load_json(path)

        start = timer()
        counter = 0

        try:
            input_data = islice(json_data, 0, c.VOTES_LIMIT)
            pool = Pool(num_threads)
            counts = pool.map(self.process_votes, input_data)
            counter = sum(counts)
        finally:
            pool.close()
            pool.join()

        end = timer()
        return counter, get_elapsed_seconds(start, end)

    def convert_meps(self, path):
        json_data = io.load_json(path)
        counter = 0

        start = timer()
        for mep in islice(json_data, 0, c.MEP_LIMIT):
            # Get raw values
            user_id = str(mep['UserID'])
            full_name = Literal(str(mep['Name']['full'].lower().title().strip()), datatype=c.STRING)
            profile_url = Literal(str(mep['meta']['url']), datatype=c.URI)
            mep_uri = self.name_to_dbr(full_name)

            # append to global dictionary
            if not self.dict_mep[user_id]:
                self.dict_mep[user_id].append(mep_uri)
            mep_uri = URIRef(mep_uri)

            if 'Photo' in mep:
                photo_url = Literal(str(mep['Photo']), datatype=c.IMAGE)
                self.dataset.add((mep_uri, c.THUMBNAIL, photo_url))

            if 'Birth' in mep:
                if 'date' in mep['Birth']:
                    birth_date = mep['Birth']['date']
                    if birth_date != '':
                        birth_date = Literal(datetime.strptime(birth_date.split('T')[0], '%Y-%m-%d').date(),
                                             datatype=c.DATE)
                        self.dataset.add((mep_uri, c.BIRTH_DATE, birth_date))

                if 'place' in mep['Birth']:
                    birth_place = URIRef(self.name_to_dbr(str(mep['Birth']['place'].strip())))
                    self.dataset.add((mep_uri, c.BIRTH_PLACE, birth_place))

            if 'Death' in mep:
                death_date = str(mep['Death'])
                death_date = Literal(datetime.strptime(death_date.split('T')[0], '%Y-%m-%d').date(), datatype=c.DATE)
                self.dataset.add((mep_uri, c.DEATH_DATE, death_date))

            # if 'active' in mep: active = mep['active'] # interesting but unused atm

            # twitter = mep['Twitter']

            # Can be expanded to process all groups. For now takes the latest known
            if 'Groups' in mep:
                # For different memberships
                # if organisationRole = mep['Groups'][0]['role'] == 'member':
                # memberOf
                # if organisationRole = mep['Groups'][0]['role'] == 'xxx':
                # xxx
                # elif organisationRole = mep['Groups'][0]['role'] == 'xxx':
                # xxx

                party_title = str(mep['Groups'][0]['Organization'])
                party_dbr = self.name_to_dbr(party_title)

                party_id = mep['Groups'][0]['groupid']
                if type(party_id) is list:
                    for pid in party_id:
                        if party_dbr not in self.dict_party[pid]:
                            self.dict_party[pid].append(party_dbr)
                    party_id = party_id[0]
                elif party_dbr not in self.dict_party[party_id]:
                    self.dict_party[party_id].append(party_dbr)


                party_uri = URIRef(str(self.dict_party[party_id][0]))
                # If a valid iri was added manually, it's always first, so just take the first
                #dataset.add((mep_uri, c.MEMBER_OF, URIRef(dict_party[party_id][0])))
                self.dataset.add((mep_uri, c.PARTY, party_uri))
                self.dataset.add((party_uri, c.IN_LEGISLATURE, c.EUROPEAN_PARLIAMENT))

            if 'Gender' in mep:
                gender = str(mep['Gender'])
                if gender == 'M':
                    self.dataset.add((mep_uri, c.GENDER, c.MALE))
                elif gender == 'F':
                    self.dataset.add((mep_uri, c.GENDER, c.FEMALE))

            self.dataset.add((mep_uri, c.FULL_NAME, full_name))
            self.dataset.add((mep_uri, c.URI, profile_url))
            self.dataset.add((mep_uri, c.OFFICE, c.MEMBER_OF_EU))

            counter += 1

        end = timer()
        return counter, get_elapsed_seconds(start, end)
