FROM python:3.11
ADD *.py .
ADD requirements.txt .
COPY utils utils/
COPY database database/
COPY bot bot/
COPY services services/
# I hate google api
RUN pip install google-cloud-translate
RUN pip install -r ./requirements.txt
EXPOSE 8080
CMD ["python", "./start_cloud.py"] 