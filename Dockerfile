FROM alpine:3.17
EXPOSE 5000
RUN mkdir /App

COPY run.sh /App/
COPY ./goodvotes /App/goodvotes
COPY requirements.txt /App/
WORKDIR /App

RUN apk add python3 bash
# RUN python3 -m venv goodvotes-env
# ENV PATH="/App/goodvotes-env/bin:$PATH"
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["bash", "run.sh"]

