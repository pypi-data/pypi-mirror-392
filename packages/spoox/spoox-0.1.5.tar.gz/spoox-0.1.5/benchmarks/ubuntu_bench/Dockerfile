FROM ubuntu:22.04

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install curl -y
RUN apt-get install wget -y
RUN apt-get install sudo -y
RUN apt-get install nano -y
RUN apt-get install cron -y
RUN apt-get install openjdk-11-jdk -y
RUN apt-get install -y python3 python3-pip python3-venv
RUN apt-get clean

RUN ln -sf /usr/bin/python3 /usr/bin/python  # now also `python` command works
RUN ln -sf /usr/bin/pip3 /usr/bin/pip  # now also `pip` command works

RUN useradd -m linus
RUN echo "linus:linus" | chpasswd
RUN echo "linus ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/linus  # sudo does not require password entry
RUN usermod -aG sudo linus
USER linus
WORKDIR /home/linus

# build image:
# 1. go to /agentu directory
# 2. execute `docker build -t ubuntu-bench-base -f src/benchmark/ubuntu_bench/docker/Dockerfile.base .`
