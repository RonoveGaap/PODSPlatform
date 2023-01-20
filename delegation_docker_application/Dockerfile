FROM gcc:4.9

ENV RAM_RESOURCES 1
ENV COMP_TYPE mut
ENV COMP_TIMES 10000
ENV IO_TYPE in
ENV IO_TIMES 1000


COPY app.cpp /usr/src/myapp/app.cpp
COPY in.txt /usr/src/myapp/in.txt
COPY test /usr/src/myapp/test
COPY json.hpp /usr/src/myapp/json.hpp
COPY script.sh /usr/src/myapp/script.sh
WORKDIR /usr/src/myapp
RUN g++ -std=c++11 -o myapp app.cpp json.hpp -lstdc++
RUN chmod +x script.sh
CMD ["/bin/bash", "./script.sh"]