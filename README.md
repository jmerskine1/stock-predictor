## For running locally

```
conda install --force-reinstall -y -q --name **your_env** -c conda-forge --file requirements.txt
```

```
python3 predict.py
```

## For running in docker

```
docker build -t stock_predictor .  
```
```
docker run --rm -v "$(pwd)/results:/app/results" stock_predictor
```

