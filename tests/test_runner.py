"""Offline regression tests for rendering, privacy boundaries and typed parameters."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('template_runner', ROOT / 'tools/run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class RunnerTests(unittest.TestCase):
    def test_missing_values_fail_before_creating_output(self):
        manifest = runner.load_manifest()
        selected = runner.select(manifest, ['Skripte/Diagnose/phi12-router-monitor.sh'])
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'rendered'
            with self.assertRaisesRegex(ValueError, 'Missing runtime values'):
                runner.render(manifest, selected, {}, target)
            self.assertFalse(target.exists())

    def test_source_scope_cannot_escape(self):
        with self.assertRaises(ValueError):
            runner.select(runner.load_manifest(), ['../../Zugangsdaten'])

    def test_invalid_addresses_and_injection_fail(self):
        for value in ('999.1.2.3', '192.0.2.1;touch /tmp/injected'):
            with self.assertRaises(ValueError):
                runner.validate('IPV4_001', value, {'type': 'ipv4'})
        with self.assertRaises(ValueError):
            runner.validate('INTERFACE_001', 'eth0; reboot', {'type': 'interface'})

    def test_python_narrative_is_quoted_as_data(self):
        text = "operator's note\nwith two lines"
        rendered = runner.validate('PYTHON_STRING_001', text, {'type': 'python_string'})
        import ast
        self.assertEqual(ast.literal_eval(rendered), text)

    def test_existing_output_is_never_overwritten(self):
        manifest = runner.load_manifest()
        selected = runner.select(manifest, ['Skripte/Diagnose/phi12-device-monitor.sh'])
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, 'already exists'):
                runner.render(manifest, selected, {}, Path(temp))

    def test_render_preserves_license_notice(self):
        manifest = runner.load_manifest()
        source = 'Skripte/Diagnose/phi12-device-monitor.sh'
        selected = runner.select(manifest, [source])
        with tempfile.TemporaryDirectory() as temp:
            output = runner.render(manifest, selected, {}, Path(temp) / 'rendered')
            notice = output / (source + '.license')
            self.assertEqual(notice.read_bytes(), (ROOT / 'templates' / (source + '.tmpl.license')).read_bytes())
            self.assertIn('GPL-2.0-or-later', notice.read_text())

if __name__ == '__main__':
    unittest.main()
