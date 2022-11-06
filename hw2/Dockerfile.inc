FROM centos:7 AS base
RUN yum clean all && yum install -y git make gcc-c++ vim ssh
RUN git clone https://github.com/python/cpython.git /opt/cpython
WORKDIR /opt/cpython
RUN git checkout 2.7

FROM base
COPY patches/inc.patch .
RUN git apply inc.patch && ./configure --with-pydebug --prefix=/tmp/python && make -j $nproc
ENTRYPOINT /bin/bash