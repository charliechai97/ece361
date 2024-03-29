/*
** talker.c -- a datagram "client" demo
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/time.h>

#define SERVERPORT "8080"    // the port users will be connecting to
#define MAXBUFLEN 100

int main(int argc, char *argv[])
{
    int sockfd;
    struct addrinfo hints, *servinfo, *p;
    int rv;
    int numbytes;
    struct sockaddr_storage their_addr;
    char buf[MAXBUFLEN];
    socklen_t addr_len;
    char s[INET6_ADDRSTRLEN];
    double totalTime[5] = {0};
    
    struct timeval start, finish;
    
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;

    if ((rv = getaddrinfo(NULL, SERVERPORT, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }
    
    // loop through all the results and make a socket
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("talker: socket");
            continue;
        }

        break;
    }

    if (p == NULL) {
        fprintf(stderr, "talker: failed to create socket\n");
        return 2;
    }
    
    
    char *myStrings[5] = {"b","bo","bor","bore","bored"};
    
    
//    if( connect(sockfd, p->ai_addr, p->ai_addrlen) == -1 ){
//        printf("didn't connect");
//        return 1;
//    }
    
    double timeincrease[4];
    
    for(int i = 0; i < 5; i++){
        gettimeofday (&start, NULL);

        if ((numbytes = sendto(sockfd, myStrings[i], strlen(myStrings[i]), 0,
                 p->ai_addr, p->ai_addrlen)) == -1) {
            perror("talker: sendto");
            exit(1);
        }
        printf("talker: sent %d bytes to %s\n", numbytes, argv[1]);

        if ((numbytes = recvfrom(sockfd, buf, MAXBUFLEN-1 , 0,
            (struct sockaddr *)&their_addr, &addr_len)) == -1) {
            perror("recvfrom");
            exit(1);
        }

        gettimeofday (&finish, NULL);
        totalTime[i] = (finish.tv_sec - start.tv_sec)*1000000L + finish.tv_usec - start.tv_usec;
        printf("%lf microseconds\n",totalTime[i]);
    }
    
    for(int i = 0; i < 4; i++){
        timeincrease[i] = totalTime[i+1] - totalTime[i];
        printf("increase: %lf microseconds\n",timeincrease[i]);
    }
    
    freeaddrinfo(servinfo);

    
    close(sockfd);

    return 0;
}