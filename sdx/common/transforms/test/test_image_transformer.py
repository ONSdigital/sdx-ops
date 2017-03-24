import datetime
import itertools
import json
import logging
import os.path
import tempfile
import unittest

import pkg_resources
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4

from sdx.common.survey import Survey
from sdx.common.test.test_transformer import PackingTests
from sdx.common.transforms.ImageTransformer import ImageTransformer
from sdx.common.transforms.PDFTransformer import PDFTransformer


class ImageTransformTests(unittest.TestCase):

    def setUp(self):
        self.max_diff, self.maxDiff = self.maxDiff, None

    def tearDown(self):
        self.maxDiff = self.max_diff

    def test_mwss_index(self):
        settings = PackingTests.Settings(
            "\\\\NP3RVWAPXX370\\SDX_preprod",
            "EDC_QImages"
        )
        log = logging.getLogger("")

        reply = json.loads(
            pkg_resources.resource_string(
                "sdx.common.test", "data/eq-mwss.json"
            ).decode("utf-8")
        )

        survey = json.loads(
            pkg_resources.resource_string(
                "sdx.common.test", "data/134.0005.json"
            ).decode("utf-8")
        )

        check = pkg_resources.resource_string(
            "sdx.common.test", "data/EDC_134_20170301_1000.csv"
        ).decode("utf-8")

        ids = Survey.identifiers(reply)._replace(
            ts=datetime.datetime(2017, 3, 7, 9, 45, 4)
        )

        with tempfile.TemporaryDirectory(prefix="sdx_") as locn:

            # Build PDF
            fp = os.path.join(locn, "pages.pdf")
            doc = SimpleDocTemplate(fp, pagesize=A4)
            doc.build(PDFTransformer.get_elements(survey, reply))

            # Create page images from PDF
            img_tfr = ImageTransformer(log, settings, survey, reply)
            images = list(img_tfr.create_image_sequence(fp, nmbr_seq=itertools.count()))

            self.assertEqual(
                check.splitlines(),
                list(img_tfr.index_lines(ids, images))
            )
