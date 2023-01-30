FROM    pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime

WORKDIR /app

COPY    ./requirements.txt  /app/
COPY    ./main.py ./anonymize.py /app/

RUN pip install -U pip && pip install -r requirements.txt 

CMD ["uvicorn", "main:app", "--port", "5000", "--host", "0.0.0.0"]
