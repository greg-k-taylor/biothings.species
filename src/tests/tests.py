import sys
import os
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from www.api.handlers import return_applist

# Add this directory to python path (contains nosetest_config)
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from biothings.tests.tests import BiothingTests
from biothings.tests.settings import BiothingTestSettings

ns = BiothingTestSettings()

class MySpeciesTest(BiothingTests):
    __test__ = True # explicitly set this to be a test class
    # Add extra nosetests here
    pass
