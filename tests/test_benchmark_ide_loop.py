import importlib.util
from importlib.machinery import SourceFileLoader
import unittest
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]


def load_benchmark_module():
    path = LAB_ROOT / "scripts" / "benchmark-ide-loop"
    loader = SourceFileLoader("benchmark_ide_loop", str(path))
    spec = importlib.util.spec_from_loader("benchmark_ide_loop", loader)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BenchmarkIdeLoopTests(unittest.TestCase):
    def test_model_smoke_flags_are_not_part_of_the_default_loop(self):
        module = load_benchmark_module()

        args = module.parse_args([])

        self.assertFalse(hasattr(args, "with_omx"))

    def test_removed_model_smoke_flag_is_rejected(self):
        module = load_benchmark_module()

        with self.assertRaises(SystemExit) as raised:
            module.parse_args(["--skip-omx"])

        self.assertEqual(raised.exception.code, 2)

    def test_waterflow_boundary_check_can_still_be_skipped(self):
        module = load_benchmark_module()

        args = module.parse_args(["--skip-waterflow-verify"])

        self.assertTrue(args.skip_waterflow_verify)


if __name__ == "__main__":
    unittest.main()
