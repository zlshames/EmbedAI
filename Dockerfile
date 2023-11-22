FROM python:3.11 as base
 
COPY ./ /app/
RUN pip install -r /app/src/requirements.txt

CMD ["python", "/app/src/privateGPT.py"]