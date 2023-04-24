FROM python:3.11
ADD *.py .
COPY utils utils/
COPY database database/
RUN pip install telebot sqlalchemy imagehash flask
EXPOSE 8080
CMD ["python", "./start_cloud.py"] 