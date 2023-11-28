FROM myubuntu

WORKDIR /home


COPY . .

# RUN python3 -m venv venv
# RUN source venv/bin/activate


RUN python3 -m pip install --upgrade pip
RUN pip install build 

RUN make install
RUN cp assets/xterm-1003 /usr/lib/terminfo/x


