
==========================
Information for Developers
==========================


Testing
-------
Running tests

::

    pytest tests

If you wish to not run the benchmarking tests (which can take some time) use

::

    pytest tests --ignore=tests/benchmarking_tests


Benchmark Testing
-----------------

For more information on benchmarking, see
`pytest-benchmark.readthedocs.io <https://pytest-benchmark.readthedocs.io/en/stable/>`__.
One can run the benchmarking tests locally with

::

    pip install pytest-benchmark
    pytest tests/benchmarking_tests

To create a local benchmark file (with which you can compare further tests),
use

::

    pytest tests/benchmarking_tests --benchmark-save="NAME"

where "NAME" should be similar to "user_date_otherinfo" for tracking purposes,
e.g., "eoghan_190321_WINpy38.json". Note that a counter is appended as a prefix
in the saved file, e.g., "0001_eoghan_190321_WINpy38.json"

Then, when you need to make sure new changes aren't regressing Shapelink, use

::

   pytest tests/benchmarking_tests --benchmark-compare="*/0001_eoghan_190321_WINpy38" --benchmark-compare-fail=median:5%



Adding a new Benchmark for Github Actions
-----------------------------------------

Shapelink uses continuous integration with GitHub Actions. The benchmarking
tests are run under the `"Benchmark with pytest-benchmark"
<https://github.com/ZELLMECHANIK-DRESDEN/shapelink/blob/main/.github/workflows/check.yml>`__
step. Any push or pull requests will trigger this step. To add a new benchmark file for GitHub
Actions, follow the steps below:

.. Note::
   GitHub Actions currently builds a matrix of OS and Python versions.
   Therefore, minor warnings will appear stating that the OS or Python versions
   don't match the current benchmark comparison files. You can ignore this
   warning. We recommend using the output from the Ubuntu-py3.8 build to create
   the new benchmark file.

1. Push your changes. Then go to the GitHub Actions build tab on GitHub. If the
   benchmarking tests passed, open the "Benchmark with pytest-benchmark"
   output.
2. Under the "===== passed =====" log, copy the contents of the `output.json`
   file and paste in a new `.json` file in your local repo in the
   `./.benchmarks/actions_benchmarks` folder. This file should be named
   as e.g., `ActionsBenchmark_190321_UBUNTUpy38.json`
3. Open the `./.github/workflows/checks.yml` file and replace the name of the
   --benchmark-compare="actions_benchmarks/ActionsBenchmark_190321_ubuntu_py38"
   to the name of your file.
4. Commit and push your changes. Now the github actions workflow will compare
   its live benchmark run to the new file you just created.
