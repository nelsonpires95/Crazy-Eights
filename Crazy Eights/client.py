import socket
import sys


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

sock = None
login = None


def connect_server():

    global sock

    print("Client trying to connect to server")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # criacao do socket TCP
    sock.connect((TCP_IP, TCP_PORT))
    print("Connected")


def send_message(msg):

    global sock

    sock.send(msg.encode("utf-8"))


def rcv_message():

    global socket

    while 1:

        data = sock.recv(BUFFER_SIZE)
        data = data.decode("utf-8")
        process_message(data)


def play():
        try:
            card_play = input("\nEscolha uma carta de 0 ao número de cartas na sua mão? \n N - para passar a vez  |  R - para pedir carta \n X - para sair \n=> ")

            if card_play == "R":
                card_play = ("REQUEST#"+login)
                send_message(card_play)
                rcv_message()

            elif card_play == "N":
                print("\nPassaste a vez.")
                card_play = ("PASS#"+login)
                send_message(card_play)
                rcv_message()

            elif card_play == "X":
                card_play = ("EXIT#"+login)
                send_message(card_play)
                exit()

            elif 0 <= int(card_play) <= 40:
                card_play = ("CARD#" + card_play + "#" +login)
                send_message(card_play)
                rcv_message()
            else:
                play()

        # vai verificar se o input é valido
        except ValueError as e:

            if not card_play:
                print("Empty!")
                play()

            elif card_play != "N":
                print("Invalid!")
                play()

            elif card_play != "R":
                print("Invalid!")
                play()

            elif card_play != "X":
                print("Invalid!")
                play()

            else:
                print("Invalid!")
                play()


def process_message(data):
    arrMessage = data.split("#")

    if arrMessage[0] == "LOGIN_OK":
        print("Login realizado com sucesso. \n Aguarde...")
        rcv_message()

    elif arrMessage[0] == "LOGIN_KO":
        print("Nick ja existente. Tente novamente.")
        do_login()

    elif arrMessage[0] == "HAND":
        player_hand = arrMessage[1].split(" ")
        print("\nYour Hand: ", end=" ")

        for i, element in enumerate(player_hand):
            print(i, end="")
            print("-", end="")
            print(element, end="  ")

        print("\n")

        #print("\nYour Hand: " + arrMessage[1])

    elif arrMessage[0] == "TOP_CARD":
        print("Top Card: " + arrMessage[1])

    elif arrMessage[0] == "YOUR_TURN":
        play()

    elif arrMessage[0] == "NOT_ACCEPTED":
        print("Carta não aceite! Jogue uma carta do mesmo valor ou naipe da Top Card ou a carta 8.")
        play()

    elif arrMessage[0] == "WIN":
        print("WINNER")
        sys.exit("O Jogo Terminou!")

    elif arrMessage[0] == "FINISH":
        print(arrMessage[1] + " venceu!!")
        sys.exit("O Jogo Terminou!")

    else:
        print("Unknown or invalid type and number of fields")


def do_login():

    global login

    login = input("Introduza o nick: ")
    send_message("LOGIN#" +login)
    msg = rcv_message()

    if (msg == "LOGIN_OK"):
        return login

    else:
        print("Error in login")
        return None

connect_server()
do_login()




