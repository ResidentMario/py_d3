## Development

### Cloning

To work on `py_d3` locally, you will need to clone it.

```git
git clone https://github.com/ResidentMario/py_d3.git
```

You can then set up your own branch version of the code, and
 work on your changes for a pull request from there.

```bash
cd my_d3
git checkout -B new-branch-name
```

### Environment

I strongly recommend creating a new virtual environment when working on `missingno` (e.g. not using the base system 
Python). You can do so with either [`conda`](https://conda.io/) or `virtualenv`. Once you have a virtual environment 
ready, I recommend running `pip install -e py_d3 .` from the root folder of the repository on your local machine.
This will create an [editable install](https://pip.pypa.io/en/latest/reference/pip_install/#editable-installs) of 
`py_d3` suitable for tweaking and further development.

### Testing

Unit tests are located in the `test` folder. I recommend using `pytest` to run them, but this is by no means required.

Any pull requests you submit should pass the existing tests.

### Data

Example data, used in the examples, is located in the `/data` folder.

## Documentation

The Quickstart section of `README.md` is the principal documentation for this package. To edit the documentation I 
recommend editing that file directly on GitHub, which will handle generating a fork and pull request for you once 
your changes are made.

The images in the documentation were generated using Jupyter Notebooks in the `notebooks/` folder and stored in 
`figures/`.