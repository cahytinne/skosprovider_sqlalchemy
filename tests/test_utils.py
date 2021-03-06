# -*- coding: utf-8 -*-

import os
import csv

import unittest

import pytest
from sqlalchemy.orm import Session
from skosprovider_sqlalchemy.models import Base, Initialiser

from skosprovider_sqlalchemy.utils import (
    import_provider,
    VisitationCalculator,
    session_factory)
from tests import DBTestCase


def _get_menu():
    from skosprovider.providers import (
        SimpleCsvProvider
    )

    ifile = open(
        os.path.join(os.path.dirname(__file__), 'data', 'menu.csv'),
        "r"
    )
    reader = csv.reader(ifile)
    csvprovider = SimpleCsvProvider(
        {'id': 'MENU'},
        reader
    )
    ifile.close()
    return csvprovider


def _get_geo():
    from skosprovider.providers import DictionaryProvider

    geo = DictionaryProvider(
        {'id': 'GEOGRAPHY'},
        [
            {
                'id': '1',
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'World'}
                ],
                'narrower': [2, 3]
            }, {
                'id': 2,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Europe'}
                ],
                'narrower': [4, 5, 10], 'broader': [1]
            }, {
                'id': 3,
                'labels': [
                    {
                        'type': 'prefLabel', 'language': 'en',
                        'label': 'North-America'
                    }
                ],
                'narrower': [6], 'broader': [1]
            }, {
                'id': 4,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Belgium'}
                ],
                'narrower': [7, 8, 9], 'broader': [2], 'related': [10]
            }, {
                'id': 5,
                'labels': [
                    {
                        'type': 'prefLabel', 'language': 'en',
                        'label': 'United Kingdom'
                    }
                ],
                'broader': [2]
            }, {
                'id': 6,
                'labels': [
                    {
                        'type': 'prefLabel', 'language': 'en',
                        'label': 'United States of America'
                    }
                ],
                'broader': [3]
            }, {
                'id': 7,
                'labels': [
                    {
                        'type': 'prefLabel',
                        'language': 'en',
                        'label': 'Flanders'
                    }
                ],
                'broader': [4]
            }, {
                'id': 8,
                'labels': [
                    {
                        'type': 'prefLabel',
                        'language': 'en',
                        'label': 'Brussels'
                    }
                ],
                'broader': [4]
            }, {
                'id': 9,
                'labels': [
                    {
                        'type': 'prefLabel',
                        'language': 'en',
                        'label': 'Wallonie'
                    }
                ],
                'broader': [4]
            }, {
                'id': 10,
                'labels': [
                    {
                        'type': 'prefLabel',
                        'language': 'nl',
                        'label': 'Nederland'
                    }
                ],
                'related': [4]
            }, {
                'id': '333',
                'type': 'collection',
                'labels': [
                    {
                        'type': 'prefLabel', 'language': 'en',
                        'label': 'Places where dutch is spoken'
                    }
                ],
                'members': ['4', '7', 8, 10]
            }
        ]
    )
    return geo


def _get_buildings():
    from skosprovider.providers import DictionaryProvider

    buildings = DictionaryProvider(
        {'id': 'BUILDINGS'},
        [
            {
                'id': '1',
                'labels': [
                    {
                        'type': 'prefLabel',
                        'language': 'en',
                        'label': 'Fortifications'
                    }
                ],
                'narrower': [2],
                'matches': {
                    'exact': ['http://vocab.getty.edu/aat/300006888']
                }
            }, {
                'id': 2,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Castle'}
                ],
                'broader': [1, 3],
                'matches': {
                    'broad': ['http://vocab.getty.edu/aat/300006888']
                }
            }, {
                'id': 3,
                'labels': [
                    {
                        'type': 'prefLabel',
                        'language': 'en',
                        'label': 'Habitations'
                    }
                ],
                'narrower': [2, 4],
                'matches': {
                    'close': ['http://vocab.getty.edu/aat/300005425']
                }
            }, {
                'id': 4,
                'labels': [
                    {'type': 'prefLabel', 'language': 'en', 'label': 'Huts'}
                ],
                'broader': [3],
                'matches': {
                    'exact': ['http://vocab.getty.edu/aat/300004824']
                }
            }
        ]
    )
    return buildings


def _get_heritage_types():
    import json

    typology_data = json.load(
        open(os.path.join(os.path.dirname(__file__), 'data', 'typologie.js')),
    )['typologie']
    from skosprovider.providers import DictionaryProvider
    from skosprovider.uri import UriPatternGenerator

    heritage_types = DictionaryProvider(
        {'id': 'HERITAGE_TYPES'},
        typology_data,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/erfgoedtypes/%s')
    )
    return heritage_types


def _get_event_types():
    import json

    event_data = json.load(
        open(os.path.join(os.path.dirname(__file__), 'data', 'gebeurtenis.js')),
    )['gebeurtenis']
    from skosprovider.providers import DictionaryProvider
    from skosprovider.uri import UriPatternGenerator

    heritage_types = DictionaryProvider(
        {'id': 'EVENT_TYPES'},
        event_data,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/gebeurtenistypes/%s')
    )
    return heritage_types


class TestImportProviderTests(DBTestCase):

    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()

    def tearDown(self):
        self.session.rollback()
        self.session.close_all()
        Base.metadata.drop_all(self.engine)

    def _get_cs(self):
        from skosprovider_sqlalchemy.models import (
            ConceptScheme as ConceptSchemeModel
        )

        return ConceptSchemeModel(
            id=68
        )

    def test_empty_provider(self):
        from skosprovider_sqlalchemy.models import (
            ConceptScheme as ConceptSchemeModel
        )
        from skosprovider.providers import DictionaryProvider

        p = DictionaryProvider({'id': 'EMPTY'}, [])
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(p, cs, self.session)
        scheme = self.session.query(ConceptSchemeModel).get(68)
        assert scheme == cs

    def test_menu(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )

        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        lobster = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 11) \
            .one()
        assert 11 == lobster.concept_id
        assert 'urn:x-skosprovider:menu:11' == lobster.uri
        assert 'Lobster Thermidor' == str(lobster.label())
        assert 1 == len(lobster.notes)

    def test_geo(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
            Collection as CollectionModel
        )

        geoprovider = _get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, cs, self.session)
        world = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 1) \
            .one()
        assert world.concept_id == 1
        assert 'urn:x-skosprovider:geography:1' == world.uri
        assert 'World' == str(world.label('en'))
        assert 1 == len(world.labels)
        assert 2 == len(world.narrower_concepts)

        dutch = self.session.query(CollectionModel) \
            .filter(CollectionModel.conceptscheme == cs) \
            .filter(CollectionModel.concept_id == 333) \
            .one()
        assert 333 == dutch.concept_id
        assert 'urn:x-skosprovider:geography:333' == dutch.uri
        assert 'collection' == dutch.type
        assert 1 == len(dutch.labels)
        assert 4 == len(dutch.members)

        netherlands = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 10) \
            .one()
        assert 10 == netherlands.concept_id
        assert 'concept' == netherlands.type
        assert 1 == len(netherlands.labels)
        assert 2 == netherlands.broader_concepts.pop().concept_id
        assert 1 == len(netherlands.related_concepts)

    def test_buildings(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )

        buildingprovider = _get_buildings()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(buildingprovider, cs, self.session)
        castle = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 2) \
            .one()
        assert 2 == len(castle.broader_concepts)
        hut = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 4) \
            .one()
        assert 1 == len(hut.broader_concepts)
        assert 1 == len(hut.matches)
        assert 'exactMatch' == hut.matches[0].matchtype_id
        assert 'http://vocab.getty.edu/aat/300004824' == hut.matches[0].uri

    def test_heritage_types(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
        )

        heritagetypesprovider = _get_heritage_types()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(heritagetypesprovider, cs, self.session)
        bomen = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 72) \
            .one()
        assert 2 == len(bomen.narrower_collections)

    def test_event_types(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel,
        )

        eventtypesprovider = _get_event_types()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(eventtypesprovider, cs, self.session)
        archeologische_opgravingen = self.session.query(ConceptModel) \
            .filter(ConceptModel.conceptscheme == cs) \
            .filter(ConceptModel.concept_id == 38) \
            .one()
        assert 3 == len(archeologische_opgravingen.narrower_collections)


class TestVisitationCalculator(DBTestCase):

    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()

    def tearDown(self):
        self.session.rollback()
        self.session.close_all()
        Base.metadata.drop_all(self.engine)

    def _get_cs(self):
        from skosprovider_sqlalchemy.models import (
            ConceptScheme as ConceptSchemeModel
        )

        return ConceptSchemeModel(
            id=1
        )

    def test_empty_provider(self):
        from skosprovider.providers import DictionaryProvider

        p = DictionaryProvider({'id': 'EMPTY'}, [])
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(p, cs, self.session)
        vc = VisitationCalculator(self.session)
        v = vc.visit(cs)
        assert 0 == len(v)

    def test_menu(self):
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert 11 == len(visit)
        for v in visit:
            assert v['lft'] + 1 == v['rght']
            assert 1 == v['depth']

    def test_menu_sorted(self):
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert 11 == len(visit)
        left = 1
        for v in visit:
            assert v['lft'] == left
            left += 2

    def test_geo(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )

        geoprovider = _get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert 10 == len(visit)
        world = visit[0]
        assert self.session.query(ConceptModel).get(world['id']).concept_id == 1
        assert 1 == world['lft']
        assert 20 == world['rght']
        assert 1 == world['depth']
        for v in visit:
            if v['id'] == 3:
                assert v['lft'] + 3 == v['rght']
                assert 2 == v['depth']
            if v['id'] == 6:
                assert v['lft'] + 1 == v['rght']
                assert 3 == v['depth']

    def test_buildings(self):
        from skosprovider_sqlalchemy.models import (
            Concept as ConceptModel
        )

        buildingprovider = _get_buildings()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(buildingprovider, cs, self.session)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert len(visit) == 5
        # Check that castle is present twice
        ids = [self.session.query(ConceptModel).get(v['id']).concept_id for v in visit]
        assert ids.count(2) == 2
        for v in visit:
            # Check that fortification has one child
            if v['id'] == 1:
                assert v['lft'] + 3 == v['rght']
                assert 1 == v['depth']
            # Check that habitations has two children
            if v['id'] == 3:
                assert v['lft'] + 5 == v['rght']
                assert 1 == v['depth']
            # Check that castle has no children
            if v['id'] == 2:
                assert v['lft'] + 1 == v['rght']
                assert 2 == v['depth']


class TestObject(object):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    @session_factory('test')
    def some_method(self):
        return self.session

    @session_factory('session_maker')
    def some_other_method(self):
        return self.session


class TestSessionFactory(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def init(self, session_maker):
        self.session_maker = session_maker

    def setUp(self):
        self.test_object = TestObject(self.session_maker)

    def test_no_session_factory_found(self):
        self.assertRaises(Exception, )
        with self.assertRaises(Exception) as cm:
            self.test_object.some_method()
        the_exception = cm.exception
        self.assertEqual(str(the_exception), 'session_maker test not found')

    def test_session_creation(self):
        res = self.test_object.some_other_method()
        self.assertIsNotNone(res)
        self.assertIsInstance(res, Session)