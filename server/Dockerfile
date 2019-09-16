FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN python -m spacy download en_core_web_sm
CMD ["python", "app.py"]