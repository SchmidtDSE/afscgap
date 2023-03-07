# Example notebooks

Notebooks which act as practical tutorials on realistic problems using `afscgap`. These can be run directly:

```
$ git checkout git@github.com:SchmidtDSE/afscgap.git
$ cd afscgap/notebooks
$ pip install -r requirements.txt
$ jupyter notebook
```

Or, one can use Docker:

```
$ git checkout git@github.com:SchmidtDSE/afscgap.git
$ cd afscgap
$ docker build --no-cache -t afscgap-notebooks .
$ docker run -it --rm -p 8888:8888 afscgap-notebooks jupyter notebook --ip=0.0.0.0 --port=8888
```
