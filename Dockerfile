FROM registry.access.redhat.com/ubi9/python-311:1-77.1725851346

USER 0

RUN mkdir /app

WORKDIR "/app"

COPY ./requirements.txt ./

RUN yum install -y mesa-libGL && \
    yum clean all && \
    rm -rf /var/cache/yum
    # python3 -m pip install --upgrade pip && \
    # python3 -m pip install -r ./requirements.txt

COPY . ./voicereplicator

WORKDIR "/app/voicereplicator"

RUN chmod -R 755 /app

EXPOSE 5000