import random
import socket
import logging
import struct

def create_header_server(seq_no, ack_no, flags):
    octeti = struct.pack("!HHB", seq_no, ack_no, flags)
    return octeti

def parse_header_server(octeti):
    seq_no, ack_no, flags = struct.unpack("!HHB",octeti)
    return seq_no, ack_no, flags

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

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

port = 5050
ip_adress = socket.gethostbyname(socket.gethostname())
server_address = (ip_adress, port)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
server.bind(server_address)

logging.info("Serverul a fost pornit pe adresa %s si portul %d", ip_adress, port)

while True:
    logging.info('Asteptam mesaje...')
    data, address = server.recvfrom(4096)
    header = data[:5]
    mesaj = data[5:]
    
    seq_no, ack_no, flag = parse_header_server(header)

    if flag == flag_syn_seq:
        logging.info('SYN: Request de SYN cu seq_no "%d" de la adresa %s ',seq_no, address)

        seq_no_client = seq_no

        seq_no2 = random.randint(seq_no,10000)
        ack_no2 = seq_no+1
        header_syn_ack = create_header_server(seq_no2, ack_no2, flag_syn_ack)

        server.settimeout(3)
        SYN_ACK = 0
        while SYN_ACK == 0:
            logging.info('SYN-ACK: Trimitem seq_no "%d" si ack_no "%d" catre %s', seq_no2, ack_no2, address)
            server.sendto(header_syn_ack, address)
            try:
                logging.info('Asteptam ACK ... ')
                data, adress = server.recvfrom(4096)
                header = data[:5]
                mesaj = data[5:]
                seq_no, ack_no, flag = parse_header_server(header)

                if flag == flag_ack:
                    SYN_ACK = 1
                else:
                    logging.info('Wrong flag received. Retrying ...')
            except socket.timeout:
                logging.info('Package lost. Retrying ...')
                continue


        logging.info('ACK: Syncronizat cu succes cu seq_no "%d" si ack_no "%d" la adresa "%s"', seq_no, ack_no, address)
        seq_no2 += 1 
        ack_no2 = seq_no + 1
        header_ack = create_header_server(seq_no2, ack_no2, flag_seq_ack)

        ACK = 0
        while ACK == 0:
            logging.info('ACK: Trimitem seq_no "%d" si ack_no "%d" catre %s', seq_no2, ack_no2, address)
            server.sendto(header_ack, address)
            try:
        
                logging.info('Asteptam raspuns ... ')
                data, adress = server.recvfrom(4096)
                header = data[:5]
                mesaj_encoded = data[5:]
                seq_no, ack_no, flag = parse_header_server(header)

                if flag == flag_seq_push:
                    ACK = 1
                else:
                    logging.info('Wrong flag received. Retrying ...')
            except socket.timeout:
                logging.info('Package lost. Retrying ...')
                continue
        
             

        while flag != flag_seq_fin:
            mesaj = mesaj_encoded.decode('utf-8')
            logging.info('PSH: Am primit mesajul: "%s"', mesaj)
            seq_no2 += 1
            ack_no2 = seq_no + 1
            header_ack = create_header_server(seq_no2, ack_no2, flag_seq_ack)

            ACK_PUSH = 0
            while ACK_PUSH == 0:
                logging.info('PSH_ACK: Trimitem seq_no "%d" si ack_no "%d" ale mesajului:  "%s"',seq_no2, ack_no2, mesaj)
                server.sendto(header_ack, address)

                try:
                    data, adress = server.recvfrom(4096)
                    header = data[:5]
                    mesaj_encoded = data[5:]
                    seq_no, ack_no, flag = parse_header_server(header)

                    if (flag == flag_seq_push and seq_no == ack_no2) or flag == flag_seq_fin:
                        ACK_PUSH = 1
                    else:
                        logging.info('Wrong flag received. Retrying ...')

                except socket.timeout:
                    logging.info('Package lost. Retrying ...')
                    continue
            
            
        
        logging.info('Am terminat de primit date')
        seq_no2 =+ 1
        ack_no2 = seq_no + 1
        header_ack = create_header_server(seq_no2, ack_no2, flag_ack_fin)

        tries = 0
        ACK_FIN = 0
        while ACK_FIN == 0:
            server.sendto(header_ack, address)
            try:
                data, adress = server.recvfrom(4096)

                ACK_FIN = 1
            except socket.timeout:
                tries += 1
                if tries == 5:
                    ACK_FIN = 1
                continue

    server.settimeout(None)
