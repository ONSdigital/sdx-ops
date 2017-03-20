from collections import OrderedDict
import io
import logging
import os
import tempfile
import zipfile

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from structlog import wrap_logger

from transform.transformers.ImageTransformer import ImageTransformer
from transform.transformers.PDFTransformer import PDFTransformer

__doc__ = """Transform MWSS survey data into formats required downstream.

The class API is used by the SDX transform service.
Additionally this module will run as a script from the command line:

python -m transform.transformers.MWSSTransformer \
< tests/replies/eq-mwss.json > test-output.zip

"""


class Transformer:

    defn = []

    @classmethod
    def ops(cls):
        """Publish the sequence of operations for the transform.

        Return an ordered mapping from question id to default value and processing function.

        """
        return OrderedDict([
            ("{0:02}".format(qNr), (dflt, fn))
            for rng, dflt, fn in cls.defn
            for qNr in (rng if isinstance(rng, range) else [rng])
        ])

    def transform(self, data, survey=None):
        """Perform a transform on survey data."""
        return OrderedDict(
            (qid, fn(qid, data, dflt, survey))
            for qid, (dflt, fn) in self.ops().items()
        )

    @staticmethod
    def create_zip(locn, manifest):
        """Create a zip archive from a local directory and a manifest list.

        Return the contents of the zip as bytes.

        """
        zip_bytes = io.BytesIO()

        with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zip_obj:
            for dst, f_name in manifest:
                zip_obj.write(os.path.join(locn, f_name), arcname=os.path.join(dst, f_name))

        zip_bytes.seek(0)
        return zip_bytes

    def __init__(self, response, seq_nr=0, log=None):
        """Create a transformer object to process a survey response."""
        self.response = response
        self.ids = Survey.identifiers(response, seq_nr=seq_nr)

        if self.ids is None:
            raise UserWarning("Missing identifiers")

        if log is None:
            self.log = wrap_logger(logging.getLogger(__name__))
        else:
            self.log = Survey.bind_logger(log, self.ids)

    def pack(self, img_seq=None):
        """Perform transformation on the survey data and pack the output into a zip file.

        Return the contents of the zip as bytes.
        The object maintains a temporary directory while the output is generated.

        """
        survey = Survey.load_survey(self.ids)
        manifest = []
        with tempfile.TemporaryDirectory(prefix="sdx_", dir="tmp") as locn:
            # Do transform and write PCK
            data = self.transform(self.response["data"], survey)
            f_name = CSFormatter.pck_name(**self.ids._asdict())
            with open(os.path.join(locn, f_name), "w") as pck:
                CSFormatter.write_pck(pck, data, **self.ids._asdict())
            manifest.append(("EDC_QData", f_name))

            # Create IDBR file
            f_name = CSFormatter.idbr_name(**self.ids._asdict())
            with open(os.path.join(locn, f_name), "w") as idbr:
                CSFormatter.write_idbr(idbr, **self.ids._asdict())
            manifest.append(("EDC_QReceipts", f_name))

            # Build PDF
            fp = os.path.join(locn, "pages.pdf")
            doc = SimpleDocTemplate(fp, pagesize=A4)
            doc.build(PDFTransformer.get_elements(survey, self.response))

            # Create page images from PDF
            img_tfr = ImageTransformer(self.log, survey, self.response)
            images = list(img_tfr.create_image_sequence(fp, nmbr_seq=img_seq))
            for img in images:
                f_name = os.path.basename(img)
                manifest.append(("EDC_QImages/Images", f_name))

            # Write image index
            index = img_tfr.create_image_index(images)
            if index is not None:
                f_name = os.path.basename(index)
                manifest.append(("EDC_QImages/Index", f_name))

            return self.create_zip(locn, manifest)
