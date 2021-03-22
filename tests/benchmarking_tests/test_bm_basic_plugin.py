
from tests import test_basic


def test_benchmark_simulator(benchmark):
    benchmark(test_basic.test_run_plugin_with_simulator, port_number="6668")
