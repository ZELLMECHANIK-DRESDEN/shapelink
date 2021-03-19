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


How to run locally:

1. To create your local benchmark data:
   pytest tests\benchmarking_tests --benchmark-save="eoghan_190321_WINpy38.json"
2. To compare with your local benchmark data (note that it doesn't save anything):
   pytest tests\benchmarking_tests --benchmark-compare="Windows-CPython-3.8-64bit\0001_eoghan_190321_WINpy38" --benchmark-compare-fail=median:5%
