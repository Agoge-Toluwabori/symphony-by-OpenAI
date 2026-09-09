import contextlib
import copy
import errno
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('canary_probe',Path(__file__).resolve().parents[1]/'canary-probe.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


def snapshot(zero=None):
    return {'real':1000,'effective':1000,'saved':1000,'parent_uid_mapping':{'0':zero,'1000':1000}}


class ProbeTests(unittest.TestCase):
    def test_expected_denials_require_unchanged_unprivileged_identity(self):
        for code in (errno.EPERM,errno.EACCES,errno.EINVAL):
            with self.subTest(code=code), patch.object(p,'identity',side_effect=[snapshot(),snapshot()]),patch.object(p.os,'setuid',side_effect=OSError(code,'fixture')):
                result=p.root_probe()
                self.assertEqual(result['status'],'DENIED')
                self.assertEqual(result['before'],result['after'])
                self.assertEqual(result['errno'],code)

    def test_errno_alone_and_unexpected_identity_are_not_proof(self):
        bad=[]
        for key in ('real','effective','saved'):
            value=snapshot();value[key]=0;bad.append(value)
            value=snapshot();value[key]=1001;bad.append(value)
        value=snapshot();value['parent_uid_mapping']['1000']=0;bad.append(value)
        for after in bad:
            with patch.object(p,'identity',side_effect=[snapshot(),after]),patch.object(p.os,'setuid',side_effect=OSError(errno.EINVAL,'fixture')):
                self.assertEqual(p.root_probe()['status'],'FAIL')
        for error in (None,OSError(errno.EIO,'fixture')):
            with patch.object(p,'identity',return_value=snapshot()),patch.object(p.os,'setuid',side_effect=error):
                self.assertEqual(p.root_probe()['status'],'UNPROVEN')
        with patch.object(p,'identity',return_value=snapshot(zero=0)),patch.object(p.os,'setuid',side_effect=OSError(errno.EINVAL,'fixture')):
            self.assertEqual(p.root_probe()['status'],'UNPROVEN')

    def test_preexisting_privilege_and_unreadable_mapping_fail_closed(self):
        for initial in (dict(snapshot(),saved=0),dict(snapshot(),parent_uid_mapping={'0':None,'1000':None})):
            with patch.object(p,'identity',return_value=initial),patch.object(p.os,'setuid') as attempt:
                self.assertEqual(p.root_probe()['status'],'FAIL');attempt.assert_not_called()
        with patch.object(p,'identity',side_effect=OSError(errno.EACCES,'fixture')),patch.object(p.os,'setuid') as attempt:
            self.assertEqual(p.root_probe()['status'],'UNPROVEN');attempt.assert_not_called()

    def test_uid_mapping_projects_only_relevant_identities(self):
        with patch.object(p.os,'getresuid',return_value=(1000,1000,1000)),patch.object(p.Path,'read_text',return_value='1000 1000 1\n9000 9999 7\n'):
            self.assertEqual(p.identity(),snapshot())
        for mapping in ('', '1000 1000 0', '1000 1000 1\n1000 9999 1'):
            with patch.object(p.os,'getresuid',return_value=(1000,1000,1000)),patch.object(p.Path,'read_text',return_value=mapping):
                with self.assertRaises(ValueError):p.identity()

    def test_einval_no_longer_skips_network_or_results(self):
        with tempfile.TemporaryDirectory() as d:
            previous=os.getcwd();os.chdir(d)
            try:
                with patch.object(p,'identity',return_value=snapshot()),patch.object(p.os,'setuid',side_effect=OSError(errno.EINVAL,'fixture')),patch.object(p.os,'open',side_effect=PermissionError()),patch.object(p.socket,'socket',side_effect=PermissionError()) as network,contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(p.main(),0)
                    network.assert_called_once()
                result=json.loads(Path('factory-containment-results.json').read_text())
                self.assertTrue(all(v=='DENIED' for v in result['checks'].values()))
                self.assertEqual(result['root_identity']['before'],result['root_identity']['after'])
            finally:os.chdir(previous)
