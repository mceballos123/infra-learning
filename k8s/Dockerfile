FROM python:3.12

WORKDIR /app

RUN apt-get update
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        python3-dev

RUN rm -rf /var/lib/apt/lists/*


COPY requirements.txt . 

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]