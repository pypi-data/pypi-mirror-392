ARG python_version=3.13
FROM helgekr/bovine:0.5.18-python${python_version}

ARG tag=0.1.6
RUN pip install roboherd[bovine]==${tag}

RUN mkdir /app
WORKDIR /app

CMD ["/bin/sh"]
