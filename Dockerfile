FROM python:3.11 as base

WORKDIR /app
COPY ./ ./
RUN pip install -r ./src/requirements.txt

CMD ["python", "./src/privateGPT.py"]