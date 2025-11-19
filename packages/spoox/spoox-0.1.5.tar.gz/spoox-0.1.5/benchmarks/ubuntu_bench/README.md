
### Run Benchmark

1. make sure the correct `Agent` is configured in `run_agent.py` 
2. go to `/agentu` directory
3. build ubuntu agentu docker image with: `docker build -t ubuntu_bench -f src/benchmark/ubuntu_bench/Dockerfile .`
4. check `TASK_IDS` in `run_benchmark.py` if correct
5. run benchmark with `python src/benchmark/ubuntu_bench/run_benchmark.py -r [num_or_runs] -d [bool_delete_all_containers_default_is_true]`
6. check logs of a specific run and task `python src/benchmark/ubuntu_bench/print_logs.py`

```bash
# using agentu in terminal
python src/agentu.py -a mas-group-chat-s -l True
```

```bash
# run benchmark
python src/benchmark/ubuntu_bench/run_benchmark.py <attr>
python src/benchmark/ubuntu_bench/print_logs.py
# checkout docker (make sure container is started)
docker exec -it <container-name> /bin/bash
```

```bash
# manually access container and run tasks
docker run -it --rm ubuntu-bench bash
# todo
```

```bash
# run a simple task and print logs
python src/benchmark/ubuntu_bench/run_task.py <attr>
```

```bash
# building entire ubuntu bench
# build base docker image
docker build -t ubuntu-bench-base -f src/benchmark/ubuntu_bench/Dockerfile .
# create and start a container based on the docker base image -> to setup a task container
docker run -it --name ubuntu-bench-task-1 plaume/ubuntu-tasks:base bash 
docker cp /Users/linus/Documents/TUM/MA/code/agentu/src/benchmark/ubuntu_bench/tasks ubuntu-bench-task-1:/opt
# ... do the setup within the container for the specific task and exit the container
# to reenter the container
docker exec -it <container-name> /bin/bash  # alternative
# finally create a docker image out of the docker container
docker commit ubuntu-bench-task-1 plaume/ubuntu-tasks:1
# upload to docker repo
docker push plaume/ubuntu-tasks:1
```

