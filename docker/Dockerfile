FROM alpine:3.17
EXPOSE 80

RUN apk add bash python3 python3-dev build-base coreutils

COPY requirements.txt .
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# create flask app
RUN mkdir /App
COPY ./docker/entrypoint.sh /App/
COPY ./goodvotes /App/goodvotes
COPY ./config /App/config

# download external css and js files
COPY ./docker/install-dependencies.sh .
RUN bash install-dependencies.sh


WORKDIR /App
CMD ["bash", "entrypoint.sh"]

