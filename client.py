from email import message
from pickle import NONE
import random
import socket
import logging
import struct

def create_header_client(seq_no, ack_no, flags):
    octeti = struct.pack("!HHB", seq_no, ack_no, flags)
    return octeti

def parse_header_client(octeti):
    seq_no, ack_no, flags = struct.unpack("!HHB",octeti)
    return seq_no, ack_no, flags


logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

port = 5050
ip_adress = socket.gethostbyname(socket.gethostname())

server_address = (ip_adress, port)

with open('input.txt') as f:
    continutFisier = f.read()

lines = continutFisier.split("\n")


flag_syn = 1 << 7
flag_seq = 1 << 6
flag_syn_seq = flag_syn + flag_seq
flag_ack = 1 << 5
flag_seq_ack = flag_seq + flag_ack
flag_syn_ack = flag_syn_seq + flag_ack
flag_psh = 1 << 4
flag_seq_push = flag_seq + flag_psh
flag_fin = 1 << 3
flag_seq_fin = flag_seq + flag_fin
flag_ack_fin = flag_seq_ack + flag_fin



seq_no1 = random.randint(0,10000)
header_syn = create_header_client(seq_no1, 0, flag_syn_seq)
empty_message = b''
payload = header_syn + empty_message

sender.settimeout(3)
SYN = 0
while SYN == 0:
    logging.info('SYN: Trimitem cerere de sincronizare cu seq_no "%d" catre %s', seq_no1, ip_adress)
    sender.sendto(payload, server_address)
    try:
        logging.info('Asteptam SYN-ACK ... ')
        data, server = sender.recvfrom(4096)
        seq_no, ack_no, flag = parse_header_client(data)
        
        if flag == flag_syn_ack:
            SYN = 1
        else:
            logging.info('Wrong flag recieved. Retrying ...')

    except socket.timeout:
        logging.info('Package lost. Retrying ...')
        continue



logging.info('SYN: Syncronizat cu succes cu ack_no "%d" la serverul "%s"', ack_no ,server)
logging.info('SYN-ACK: Request de SYN cu seq_no "%d" la adresa "%s"', seq_no,  server)
ack_no1 = seq_no + 1
seq_no1 += 1
header_ack = create_header_client(seq_no1, ack_no1, flag_ack)
payload = header_ack + empty_message


ACK = 0
while ACK == 0:
    logging.info('ACK: Trimitem seq_no "%d" si ack_no "%d" catre %s', seq_no1, ack_no1, server)
    sender.sendto(payload, server)
    try:
        logging.info('Asteptam ACK ca serverul a primit ACK ... ')
        data, server = sender.recvfrom(4096)
        seq_no, ack_no, flag = parse_header_client(data)

        if flag == flag_seq_ack:
            ACK = 1
        else:
            logging.info('Wrong flag received. Retrying ...')

    except socket.timeout:
        logging.info('Package lost. Retrying ...')
        continue


logging.info('Putem incepe data stream-ul')
for line in lines:
    mesaj = line.encode('utf-8')
    seq_no1 += 1
    header_fara_mesaj = create_header_client(seq_no1, 0, flag_seq_push)
    payload = header_fara_mesaj + mesaj

    PUSH = 0
    while PUSH == 0:
        logging.info('PSH: Trimitem mesajul "%s" cu seq_no "%d" catre %s', line, seq_no1, server)
        sender.sendto(payload, server)

        try:
            logging.info('Asteptam raspuns ... ')
            data, server = sender.recvfrom(4096)
            seq_no, ack_no, flag = parse_header_client(data)

            if flag == flag_seq_ack and ack_no == seq_no1+1:
                PUSH = 1
            else:
                logging.info('Wrong flag received. Retrying ...')

        except socket.timeout:
            logging.info('Package lost. Retrying ...')
            continue
    print(seq_no, ack_no, flag)
        

seq_no1 += 1
header_fin = create_header_client(seq_no1, 0, flag_seq_fin)
payload = header_fin + empty_message

FIN = 0
while FIN == 0:
    logging.info('FIN: Trimitem flag-ul de FIN la server %s', server)
    sender.sendto(payload, server)
    try:
        logging.info('Asteptam raspuns ... ')
        data, server = sender.recvfrom(4096)
        seq_no, ack_no, flag = parse_header_client(data)

        if flag == flag_ack_fin:
            FIN = 1
        else:
            logging.info('Wrong flag received. Retrying ...')

    except socket.timeout:
        logging.info('Package lost. Retrying ...')
        continue


logging.info('closing socket')
sender.close()



# Trebuie adaugat un sleep/timeout daca nu primeste date si facut sa retrimita pachetul daca ajunge la timeout
# exemplu:
#
# import socket
# from socket import AF_INET, SOCK_DGRAM
#
# def main():
#     client_socket = socket.socket(AF_INET, SOCK_DGRAM)
#     client_socket.settimeout(1)
#     server_host = 'localhost'
#     server_port = 1234
#     while(True):
#         client_socket.sendto('Message', (server_host, server_port))
#         try:
#             reply, server_address_info = client_socket.recvfrom(1024)
#             print reply
#         except socket.timeout:
#             #more code