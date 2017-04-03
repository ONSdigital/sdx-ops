#!/usr/bin/env python
#   coding: UTF-8

import argparse
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

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.packages.urllib3.util.retry import Retry

from sdx.common.survey import Survey
from sdx.common.transforms.PDFTransformer import PDFTransformer

__doc__ = """
The SDX Image Transformer:

"""


class ImageTransformer(object):

    session = requests.Session()

    @staticmethod
    def extract_pdf_images(path, f_name):
        """Extract pages from a PDF document.

        :param str path: The location of the working directory.
        :param str f_name: The file name of the PDF document.
        :return: A sorted sequence of image file names.

        This method delegates to the *pdftoppm* utility.

        """
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
        """Renumber the image sequence extracted from pdf

        :param str path: The location of the working directory.
        :param nmbr_seq: A sequence or generator of integers.
        :type nmbr_seq: list or generator.
        :return: A generator of file paths.

        """
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
                ids.ts.strftime("%d/%m/%Y %H:%M:%S"),
                "\\".join([
                    self.settings.FTP_HOST,
                    self.settings.SDX_FTP_IMAGE_PATH,
                    "Images",
                    os.path.basename(img)
                ]),
                ids.ts.strftime("%Y%m%d"),
                os.path.splitext(os.path.basename(img))[0],
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
            self.logger.info(
                "Returned from sdx-sequence",
                request_url=res.url,
                status=res.status_code
            )
            return True
        else:
            self.logger.error(
                "Returned from sdx-sequence",
                request_url=res.url,
                status=res.status_code
            )
            return False

    def remote_call(self, request_url, json=None):
        try:
            self.logger.info("Calling sdx-sequence", request_url=request_url)

            r = None

            if json:
                r = self.session.post(request_url, json=json)
            else:
                r = self.session.get(request_url)

            return r
        except MaxRetryError:
            self.logger.error("Max retries exceeded (5)", request_url=request_url)

    def get_image_sequence_no(self):
        sequence_url = self.settings.SDX_SEQUENCE_URL + "/image-sequence"

        r = self.remote_call(sequence_url)

        if not self.response_ok(r):
            return False

        result = r.json()
        return result['sequence_no']
