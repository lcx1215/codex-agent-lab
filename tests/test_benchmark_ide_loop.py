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
    def test_model_smoke_is_enabled_by_default(self):
        module = load_benchmark_module()

        args = module.parse_args([])

        self.assertTrue(args.with_omx)

    def test_model_smoke_can_be_explicitly_skipped(self):
        module = load_benchmark_module()

        args = module.parse_args(["--skip-omx"])

        self.assertFalse(args.with_omx)


if __name__ == "__main__":
    unittest.main()
