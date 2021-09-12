#!/usr/bin/env python3

import shutil
import subprocess
import unittest

from src.hentai import get_logfile_path

remove_file = lambda file: file.unlink() if file.exists() else None

class TestHentaiCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tiny_evil_id = 269582

    def test_cli_download(self):
        call = subprocess.call("hentai download --id %s --no-check" % self.tiny_evil_id, shell=True)
        self.assertFalse(call, msg="Download failed for ID=%d" % self.tiny_evil_id)

    def test_cli_preview(self):
        print()
        call = subprocess.call("hentai preview --id %d" % self.tiny_evil_id, shell=True)
        self.assertFalse(call, msg="Preview failed for ID=%d" % self.tiny_evil_id)

    def test_cli_log(self):
        print()
        call = subprocess.call("hentai log --read", shell=True)
        self.assertTrue(get_logfile_path().exists() and (call == 0), msg="No log file was produced in '%s'" % str(get_logfile_path()))

    @classmethod
    def tearDownClass(cls):
        remove_file(get_logfile_path())
        shutil.rmtree(str(cls.tiny_evil_id), ignore_errors=True)
