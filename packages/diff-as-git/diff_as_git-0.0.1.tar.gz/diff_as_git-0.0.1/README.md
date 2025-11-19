
# Python git diff clone

This lib is an implementation of the `git diff` tool in Python using the Myers Difference algorithm.

## Usage

You can run the following command:

```bash
$ python diff.py case_one.txt case_two.txt 
```

This will show the diff script to go from file A to file B. You can test out the command with the `case_one.txt` and `case_two.txt` files included in the repository.

To have the command available at all times, make sure the script `diff.py` is executable and then include it in your `$PATH`.

## Analysis

For an extended analysis, refer to the PDF in this repo titled "The Myers Difference Algorithm for Version Control Systems".


### generete lib: python setup.py sdist 

### send to pypi: twine upload dist/*