# Example notebooks
Notebooks which act as practical tutorials on realistic problems using `afscgap`. There are multiple options to run these notebooks.

<br>

### MyBinder
One can run example code in a hosted cloud notebook environment at [MyBinder](https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb).

<br>

### Docker
We provide a Docker image to run a Jupyter notebook server in a VM with all of the dependencies installed.

```
$ git checkout git@github.com:SchmidtDSE/afscgap.git
$ cd afscgap
$ docker build --no-cache -t afscgap-notebooks .
$ docker run -it --rm -p 8888:8888 afscgap-notebooks jupyter notebook --ip=0.0.0.0 --port=8888
```

Simply ctrl-c when done to close the notebook server and Docker instance.

<br>

### Run manually
One can run manually with the following:

```
$ git checkout git@github.com:SchmidtDSE/afscgap.git
$ cd afscgap/notebooks
$ pip install -r requirements.txt
$ jupyter notebook
```

Cartopy may present some challenges for installation in some environments. Note that you can use a [pre-built wheel](https://scitools.org.uk/cartopy/docs/v0.20/installing.html#conda-pre-built-binaries) or [third-party build](https://scitools.org.uk/cartopy/docs/v0.20/installing.html#other-pre-built-binaries) as well if you run into issues when using Cartopy from source.
