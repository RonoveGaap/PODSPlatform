 cd UDado
 docker build . -t padec/microdado
 cd ..
 cd delegation_docker_application
 docker build . -t padec/performanceapp
 cd ..
 cd DataInterceptor
 docker build . -t padec/interceptor
 cd ..
