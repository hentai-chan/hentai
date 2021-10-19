#!/usr/bin/env python3

import shutil
import subprocess
import unittest

from src.hentai import get_logfile_path

class TestHentaiCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.holo_id = 308592

    def test_cli_download(self):
        call = subprocess.call("hentai download --id %s --no-check" % self.holo_id, shell=True)
        self.assertFalse(call, msg="Download failed for ID=%d" % self.holo_id)

    def test_cli_preview(self):
        print()
        call = subprocess.call("hentai preview --id %d" % self.holo_id, shell=True)
        self.assertFalse(call, msg="Preview failed for ID=%d" % self.holo_id)

    def test_cli_log(self):
        print()
        call = subprocess.call("hentai log --list", shell=True)
        self.assertTrue(get_logfile_path().exists() and (call == 0), msg="No log file was produced in '%s'" % str(get_logfile_path()))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(str(cls.holo_id), ignore_errors=True)
