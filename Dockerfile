FROM apache/airflow:latest-python3.8

RUN pip install --user --upgrade pip

RUN pip install --upgrade setuptools

RUN pip install ez_setup

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt