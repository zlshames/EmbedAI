FROM python:3.11 as base

WORKDIR /app
COPY ./ ./
RUN pip install -r /app/src/requirements.txt

CMD ["python", "./src/privateGPT.py"]