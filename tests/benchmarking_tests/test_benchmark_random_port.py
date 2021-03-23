
from tests import test_random_port


def test_benchmark_simulator(benchmark):
    benchmark(test_random_port.test_run_plugin_with_random_port,
              random_port=True)
