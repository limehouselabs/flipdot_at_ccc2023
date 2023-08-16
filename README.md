# Flipdot

## Useage

```
> docker build -t flipdot .
> docker run -p 8000:8000 flipdot
```

in a separate terminal:
```
> docker exec -ti $(docker ps -q) poetry run python ./drawtext.py --fake 
# NB this assumes you're not running anything else in docker
```

navigate to [localhost:8000/flipdot](http://localhost:8000/flipdot)
