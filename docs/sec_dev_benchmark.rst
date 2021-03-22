
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

For more information on benchmarking, see the
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

   pytest tests/benchmarking_tests --benchmark-compare="*\0001_eoghan_190321_WINpy38" --benchmark-compare-fail=median:5%



Adding a new Benchmark for Github Actions
-----------------------------------------


How to create/update the .benchmarks folder with new
github actions pytest-benchmark .json files.

1. All workflows now output the contents of the live benchmark speed
   test under the "Benchmark with pytest-benchmark" Github Actions step.
   You may need to rerun the actions to make it pass. This issue should be brought up in
   the pytest-benchmarks github and the github actions repo
2. Copy the contents of the output.json file and place in a new json file in the
   ./.github/workflows folder.
3. Open the ./.github/workflows/checks.yml file and replace the name of the
   --benchmark-compare="actions_benchmarks/ActionsBenchmark_190321_ubuntu_py38"
   to the name of your file.
4. push the changes. Now the github actions workflow will compare its
   live benchmark run to the new file


Note: we have a matrix of OS and py versions running, but this will only cause
a minor warning in the log output of github actions, just use the ubuntu py38 output json
