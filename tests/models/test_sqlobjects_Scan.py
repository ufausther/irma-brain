from unittest import TestCase
from mock import MagicMock
from random import randint

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from brain.models.sqlobjects import Scan
from lib.irma.common.utils import IrmaScanStatus
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound


class TestModelsScan(TestCase):
    def setUp(self):
        self.frontend_scanid = "frontend_scanid"
        self.nb_files = randint(10, 20)
        self.user_id = "user_id"
        self.session = MagicMock()

    def test001___init__(self):
        scan = Scan(self.frontend_scanid, self.user_id, self.nb_files)
        self.assertEqual(scan.scan_id, self.frontend_scanid)
        self.assertEqual(scan.user_id, self.user_id)
        self.assertEqual(scan.nb_files, self.nb_files)
        self.assertEqual(scan.status, IrmaScanStatus.empty)
        self.assertIsNotNone(scan.timestamp)

    def test002_get_scan(self):
        scan_id = "scan_id"
        Scan.get_scan(scan_id, self.user_id, self.session)
        self.session.query.assert_called_once_with(Scan)
        m_filter = self.session.query(Scan).filter
        m_filter.assert_called_once()
        m_filter().one.assert_called_once()

    def test003_get_scan_not_found(self):
        self.session.query.side_effect = NoResultFound
        with self.assertRaises(IrmaDatabaseResultNotFound):
            Scan.get_scan("whatever", self.user_id, self.session)

    def test004_get_scan_multiple_found(self):
        self.session.query.side_effect = MultipleResultsFound
        with self.assertRaises(IrmaDatabaseError):
            Scan.get_scan("whatever", self.user_id, self.session)
