# UDP with 3-way handshake

This project implements the Reliable UDP protocol by providing reliability via a 3-way handshake.


The header is extended to contain the sequence number in 2 bytes, acknowledgement number in another 2 bytes as well as the 5 flags on 5 bits, with the 3 remaining bits of the 5th byte empty.
  - The SYN flag signifies a request for syncronization to the target server.
  - The SEQ flag indicates the existance of a sequence number that will be used for further communication.
  - The ACK flag signifies the acknowledgement of recieving a file.
  - The PSH flag is used to signal data transfer.
  - The FIN flag marks the end of transmission and the termination of the connection.

 ![alt text](https://i.imgur.com/qGRZ70H.png)
 
 ![alt text](https://i.imgur.com/x4MUJMW.png)
 
 The client sends a SYN request to the server with a random sequence number.
 
 The server then answers with an ACK request with the acknowledgement number being the client's sequence number + 1.
 
 The server also sends a SYN request to the client with another random sequence number.
 
 The client responds to the ACK in the same fashion, with the acknowledgement number being the server's sequence number + 1.
 
 The transmission of files may then proceed until a FIN flag is sent.
 
 The server also must confirm that it has recieved every individual file for the client to send the next one.

 If at any point any packet is lost and an answer is not recieved in the timeout period or the wrong answer is recieved by either server, the packet is sent again.

 In order to simulate packet loss, tc qdisc was used.
