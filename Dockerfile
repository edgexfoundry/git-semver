FROM golang:1.11-alpine AS build

RUN set -x \
 && apk add --no-cache \
    git \
    openssh-client
ENV CGO_ENABLED=0
ENV GO111MODULE=on
WORKDIR /go/src/git-semver
COPY . .
RUN go build -v -o /usr/local/bin/git-semver

FROM alpine:3.9

RUN set -x \
 && apk add --no-cache \
    git \
    openssh-client \
    netcat-openbsd

COPY --from=build /usr/local/bin/git-semver /usr/local/bin/
