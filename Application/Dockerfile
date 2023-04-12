FROM alpine:3.17
RUN apk add python3 tree bash
RUN mkdir /GoodVotesApp
COPY . /GoodVotesApp/
RUN tree -a /GoodVotesApp/
WORKDIR /GoodVotesApp/Server
RUN python3 -m ensurepip
RUN python3 -m pip install Flask
RUN python3 -m pip install waitress
CMD ["bash", "run.sh"]
EXPOSE 5000
