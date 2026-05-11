import importlib.util
from pathlib import Path
import random
import sys
import types
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "server-bench.py"


def install_stub_modules():
    datasets = types.ModuleType("datasets")
    datasets.load_dataset = lambda *args, **kwargs: {"test": {"question": ["alpha", "beta", "gamma"]}}
    sys.modules["datasets"] = datasets

    matplotlib = types.ModuleType("matplotlib")
    pyplot = types.ModuleType("matplotlib.pyplot")
    sys.modules["matplotlib"] = matplotlib
    sys.modules["matplotlib.pyplot"] = pyplot

    numpy = types.ModuleType("numpy")
    sys.modules["numpy"] = numpy

    requests = types.ModuleType("requests")
    requests.ConnectionError = ConnectionError
    requests.adapters = types.SimpleNamespace(HTTPAdapter=object)
    requests.Session = object
    sys.modules["requests"] = requests

    tqdm = types.ModuleType("tqdm")
    tqdm_contrib = types.ModuleType("tqdm.contrib")
    tqdm_concurrent = types.ModuleType("tqdm.contrib.concurrent")
    tqdm_concurrent.thread_map = lambda func, data, **kwargs: [func(item) for item in data]
    sys.modules["tqdm"] = tqdm
    sys.modules["tqdm.contrib"] = tqdm_contrib
    sys.modules["tqdm.contrib.concurrent"] = tqdm_concurrent


def load_server_bench():
    install_stub_modules()
    spec = importlib.util.spec_from_file_location("server_bench", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ServerBenchHelpersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_bench = load_server_bench()

    def test_get_prompt_lengths_rng_is_deterministic_with_seed_offset(self):
        first = self.server_bench.get_prompt_lengths_rng(5, 4, 9, seed_offset=7)
        second = self.server_bench.get_prompt_lengths_rng(5, 4, 9, seed_offset=7)

        self.assertEqual(first, second)
        self.assertTrue(all(4 <= value <= 9 for value in first))

    def test_get_prompt_lengths_rng_matches_documented_seed_formula(self):
        expected = []
        for i in range(3):
            random.seed(3 * (11 + 1000 * i) + 0)
            expected.append(random.randint(10, 20))

        self.assertEqual(expected, self.server_bench.get_prompt_lengths_rng(3, 10, 20, seed_offset=11))

    def test_get_prompts_rng_respects_requested_lengths_and_token_bounds(self):
        random.seed(123)
        prompts = self.server_bench.get_prompts_rng([0, 1, 4])

        self.assertEqual([0, 1, 4], [len(prompt) for prompt in prompts])
        self.assertTrue(all(100 <= token <= 10000 for prompt in prompts for token in prompt))

    def test_get_prompts_text_loads_mmlu_and_honors_limit(self):
        self.assertEqual(["alpha", "beta"], self.server_bench.get_prompts_text("MMLU", 2))
        self.assertEqual(["alpha", "beta", "gamma"], self.server_bench.get_prompts_text("mmlu", -1))

    def test_get_prompts_text_rejects_unknown_dataset(self):
        self.assertIsNone(self.server_bench.get_prompts_text("rng-4-8", 3))


if __name__ == "__main__":
    unittest.main()
