FROM python:3.10-bullseye
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
STOPSIGNAL SIGINT
CMD ["python3", "bot.py"]
