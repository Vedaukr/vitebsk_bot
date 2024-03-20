FROM python:3.11-slim
COPY . ./

# ffmpeg for pydub
RUN apt-get -y update \
    && pip install -r ./requirements.txt

EXPOSE 8080
CMD ["python", "./start_cloud.py"] 