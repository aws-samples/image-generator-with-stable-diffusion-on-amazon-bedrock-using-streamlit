FROM public.ecr.aws/docker/library/python:3.11.6-slim

WORKDIR /apps
COPY apps/ .
RUN apt update && apt install git -y && \
   pip install -r requirements.txt
   
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app.py" ]
