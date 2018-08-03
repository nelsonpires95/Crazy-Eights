import socket
import threading
import random
import time
import sys


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # criacao do socket TCP
sock.bind((TCP_IP, TCP_PORT))
sock.settimeout(10)
sock.listen(1)

# simbolos dos naipes
CLUBS = "\u2663"
HEARTS = "\u2665"
DIAMONDS = "\u2666"
SPADES = "\u2660"

ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
suits = (CLUBS, SPADES, DIAMONDS, HEARTS)

deck = [r+s for r in ranks for s in suits]      # deck de cartas
hand_size = 5       # cartas por mao - inicial
clients = dict()        # dicionario
played = False      # flag para saber se o jogador jogou
top_card = ""       # carta voltada para cima
winner = False      # flag para verificar se o jogo acaba se alguem ganhar


# distibui cartas iniciais aos jogadores
def deal(clients, deck, hand_size):

    random.shuffle(deck)        # baralha as cartas do deck

    for player in clients:
        conn = clients[player][0]
        hand = []       # cria um array por cada jogador

        for i in range(0, hand_size):
            hand.append(deck.pop())    # adiciona 5 cartas ao array

        clients[player].append(hand)        # adiciona outro value à key player
        player_hand = " ".join(hand)        # tranforma o array em string para o send_message funcionar
        send_message("HAND#"+player_hand, conn)     # envia a mao ao jogador


# envia a top card para cada jogador
def topCard(top_card2):

    global top_card

    for player in list(clients):
        conn = clients[player][0]
        top_card == top_card2
        send_message("TOP_CARD#"+top_card2, conn)


def play():

    global played, top_card

    deal(clients, deck, hand_size)      # distribui as cartas
    top_card = deck.pop()       # top card inicial
    topCard(top_card)

    while not winner:

        for player, number in clients.copy().items():       # cria copia da list player para poder remover players
            send_message("YOUR_TURN", clients[player][0])
            played = False

            while not played and not winner:
                print("Espera da jogada")
                time.sleep(5)


def win(player):

    global clients, winner

    # verifica caso exista apenas 1 jogador termina o jogo
    if len(clients) == 1:
        client = list(clients)[0]
        send_message("WIN#", clients[client][0])
        winner = True
        sys.exit(0)

    # verifica se o player não tem cartas na mao
    elif len(clients[player][1]) == 0:
        send_message("WIN#", clients[player][0])
        for playerrr in clients:
            send_message("FINISH#" + player, clients[playerrr][0])
        winner = True
        sys.exit(0)


# processa as mensagens recebidas dos jogadores
def process_message(arrMessage, conn):

    global played, winner

    if arrMessage[0] == "LOGIN" and len(arrMessage) == 2:
        print("Type: login => " + arrMessage[1])

        if arrMessage[1] not in clients.keys():
            clients.setdefault(arrMessage[1], []).append(conn)
            print("New player logged in: " + arrMessage[1])
            send_message("LOGIN_OK", conn)
        else:
            print("Username already in use: " + arrMessage[1])
            send_message("LOGIN_KO", conn)

    elif arrMessage[0] == "CARD":
        testCardPlay(arrMessage[1], arrMessage[2])
        win(arrMessage[2])
        played = True

    elif arrMessage[0] == "PASS":
        print("Jogador Passou a Vez")
        played = True

    elif arrMessage[0] == "EXIT":
        print("Jogador Saiu")
        played = True
        deck.extend(clients[arrMessage[1]][1]) #adiciona as cartas do jogador que sai ao deck
        del clients[arrMessage[1]]
        win(arrMessage[1])

    elif arrMessage[0] == "REQUEST":
        print("O jogador pediu carta")
        clients[arrMessage[1]][1].append(deck.pop())
        player_hand = " ".join(clients[arrMessage[1]][1])
        send_message("HAND#" + player_hand, conn)
        send_message("TOP_CARD#" + top_card, conn)
        time.sleep(2)
        send_message("YOUR_TURN#", conn)

    elif winner:
        print("Acabou o jogo")
        sys.exit(0)

    else:
        print("Unknown or invalid type and number of fields")


# remove a carta da mao do jogador
def remove_card(card, player):

    global top_card

    top_card = clients[player][1].pop(int(card))        # remove a carta da mao do jogador e passa essa carta para top_card
    deck.insert(0, top_card)        # coloca a carta no início do deck para não se acabarem as cartas do deck
    player_hand = " ".join(clients[player][1])
    send_message("HAND#"+player_hand, clients[player][0])


def testCardPlay(card, player):

    global top_card, played

    playerCard = clients[player][1][int(card)]

    # retirar o "1" caso as cartas sejam o 10 ficando assim o tamanho da string sempre igual a 2
    if len(top_card) == 3:
        top_card = top_card[1:]
    if len(playerCard) == 3:
        playerCard = playerCard[1:]

    if playerCard[0] == top_card[0] or playerCard[1] == top_card[1] or playerCard[0] == "8":
        remove_card(card, player)
        topCard(top_card)

    else:
        send_message("NOT_ACCEPTED#", clients[player][0])
        print("Not accepted Card")


# metodo de enviar mensagens
def send_message(msg, conn):
    conn.send(msg.encode("utf-8"))
    print("Message sent: " + msg)


def client(conn, addr):

    print("Client thread: " + str(addr))

    try:
        while 1:
            data = conn.recv(BUFFER_SIZE)
            data = data.decode("utf-8")
            arrClients = data.split("#")
            process_message(arrClients, conn)

    except ConnectionResetError:
            print("Jogador desligou!")

            for k, v in clients.items():
                if conn == v or isinstance(v, list) and conn in v:
                    print(k)
                    data=("EXIT#"+k)
                    arrClients = data.split("#")
                    process_message(arrClients, conn)
    # conn.close()


while not winner:

    if 2 <= len(clients) < 6:
        print("-----------------")
        start_game = input("Deseja comecar a jogar? S/N")
        if start_game == "S":
            play()

    elif len(clients)==6:
        play()

    else:

        print("Waiting for clients...")
        try:
            conn, addr = sock.accept()      # aceita a ligacao
            print("Connection Adress: " + str(addr))

            t = threading.Thread(target=client, args=(conn, addr))
            t.start()
        except socket.timeout:
            continue