FROM alpine:3.17
EXPOSE 5000
RUN mkdir /App

RUN apk add python3 bash
RUN python3 -m ensurepip
RUN pip install -r requirements.txt
RUN pip install waitress

COPY run.sh /App/
COPY ./goodvotes /App/goodvotes
WORKDIR /App

CMD ["bash", "run.sh"]

