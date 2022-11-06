FROM centos:7
RUN yum clean all && yum install -y git make gcc-c++ vim ssh
RUN git clone https://github.com/python/cpython.git /opt/cpython
WORKDIR /opt/cpython
RUN git checkout 2.7
COPY patches .
RUN ./configure --with-pydebug --prefix=/tmp/python && make -j $nproc
ENTRYPOINT /bin/bash