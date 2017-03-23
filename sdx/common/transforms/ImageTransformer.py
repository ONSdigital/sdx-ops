#!/usr/bin/env python
#   coding: UTF-8

import argparse
import datetime
import dateutil.parser
import glob
from io import BytesIO
import itertools
import json
import logging
import os.path
import shutil
import subprocess
import sys
import zipfile

import arrow
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.packages.urllib3.util.retry import Retry

from sdx.common.survey import Survey
from sdx.common.transforms.PDFTransformer import PDFTransformer

__doc__ = """
SDX Image Transformer.

Example:

python -m transform.transformers.ImageTransformer --survey transform/surveys/144.0001.json \\
< tests/replies/ukis-01.json > output.zip

"""


class ImageTransformer(object):

    session = requests.Session()

    @staticmethod
    def create_pdf(survey, data):
        '''
        Create a pdf which will be used as the basis for images
        '''
        pdf_transformer = PDFTransformer(survey, data)
        return pdf_transformer.render_to_file()

    @staticmethod
    def extract_pdf_images(path, f_name):
        '''
        Extract all pdf pages as jpegs
        '''
        rootName, _ = os.path.splitext(f_name)
        subprocess.call(
            ["pdftoppm", "-jpeg", f_name, rootName],
            cwd=path
        )
        return sorted(glob.glob("%s/%s-*.jpg" % (path, rootName)))

    def __init__(self, logger, settings, survey, response_data, sequence_no=1000):
        self.logger = logger
        self.settings = settings
        self.survey = survey
        self.response = response_data
        self.sequence_no = sequence_no

        adapter = self.session.adapters["http://"]
        if adapter.max_retries.total != 5:
            retries = Retry(total=5, backoff_factor=0.1)
            self.session.mount("http://", HTTPAdapter(max_retries=retries))
            self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_image_sequence_numbers(self):
        sequence_numbers = []
        for image in self.images:
            sequence_number = self.get_image_sequence_no()
            sequence_numbers.append(sequence_number)

        self.logger.debug('Sequence numbers generated', sequence_numbers=sequence_numbers)
        return sequence_numbers

    def create_image_sequence(self, path, nmbr_seq=None):
        '''
        Renumber the image sequence extracted from pdf
        '''
        locn, baseName = os.path.split(path)
        self.images = ImageTransformer.extract_pdf_images(locn, baseName)
        nmbr_seq = nmbr_seq or self.get_image_sequence_numbers()
        for imageFile, n in zip(self.images, nmbr_seq):
            name = "S%09d.JPG" % n
            fp = os.path.join(locn, name)
            os.rename(imageFile, fp)
            yield fp

    def index_lines(self, ids, images):
        return (
            ",".join([
                ids.ts.strftime("DD/MM/YYYY HH:mm:ss"),
                "\\".join([self.settings.SDX_FTP_IMAGE_PATH, img]),
                ids.ts.strftime("YYYYMMDD"),
                os.path.splitext(img)[0],
                ids.survey_id,
                ids.inst_id,
                ids.ru_ref,
                Survey.parse_timestamp(ids.period).strftime("%Y%m"),
                "{0:03}".format(n + 1) if n else "001,0"
            ])
            for n, img in enumerate(images)
        )

    def create_image_index(self, images):
        '''
        Takes a list of images and creates a index csv from them
        '''
        if not images:
            return None

        ids = Survey.identifiers(self.response)
        image_path = self.settings.FTP_HOST + self.settings.SDX_FTP_IMAGE_PATH + "\\Images"

        for i in images:
            self.logger.info("Adding image to index", file=(image_path + os.path.basename(i)))

        self.index_file = "EDC_{0}_{1}_{2:04}.csv".format(
            ids.survey_id,
            ids.user_ts.strftime("%Y%m%d"),
            self.sequence_no
        )

        locn = os.path.dirname(images[0])
        path = os.path.join(locn, self.index_file)
        with open(path, "w") as fh:
            fh.write("\n".join(self.index_lines(ids, images)))
        return path

    def create_zip(self, images, index):
        '''
        Create a zip from a renumbered sequence
        '''
        in_memory_zip = BytesIO()

        with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for fp in images:
                f_name = os.path.basename(fp)
                try:
                    zipf.write(fp, arcname=f_name)
                except Exception as e:
                    self.logger.error(e)

            if index:
                f_name = os.path.basename(index)
                zipf.write(index, arcname=f_name)

        # Return to beginning of file
        in_memory_zip.seek(0)

        return in_memory_zip

    def cleanup(self, locn):
        '''
        Remove all temporary files, by removing top level dir
        '''
        shutil.rmtree(locn)

    def response_ok(self, res):

        if res.status_code == 200:
            self.logger.info("Returned from sdx-sequence", request_url=res.url, status=res.status_code)
            return True
        else:
            self.logger.error("Returned from sdx-sequence", request_url=res.url, status=res.status_code)
            return False

    def remote_call(self, request_url, json=None):
        try:
            self.logger.info("Calling sdx-sequence", request_url=request_url)

            r = None

            if json:
                r = session.post(request_url, json=json)
            else:
                r = session.get(request_url)

            return r
        except MaxRetryError:
            self.logger.error("Max retries exceeded (5)", request_url=request_url)

    def get_image_sequence_no(self):
        sequence_url = settings.SDX_SEQUENCE_URL + "/image-sequence"

        r = self.remote_call(sequence_url)

        if not self.response_ok(r):
            return False

        result = r.json()
        return result['sequence_no']


def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
    )
    rv.add_argument(
        "--survey", required=True,
        help="Set a path to the survey JSON file.")
    return rv


def main(args):
    log = logging.getLogger("ImageTransformer")
    fp = os.path.expanduser(os.path.abspath(args.survey))
    with open(fp, "r") as f_obj:
        survey = json.load(f_obj)

    data = json.load(sys.stdin)
    tx = ImageTransformer(log, survey, data)
    path = tx.create_pdf(survey, data)
    images = list(tx.create_image_sequence(path, nmbr_seq=itertools.count()))
    index = tx.create_image_index(images)
    zipfile = tx.create_zip(images, index)
    sys.stdout.write(zipfile)
    return 0


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
