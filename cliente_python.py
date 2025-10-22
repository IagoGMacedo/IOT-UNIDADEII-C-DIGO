# cliente_python.py
import xmpp
import time
import paho.mqtt.client as mqtt # Importa a biblioteca MQTT

JID = 'usuario1@localhost'    # JID para este script
PASSWORD = '123'           # Senha do usuario_chat
SERVER = 'localhost'
PORT = 5223                     

#Configurações MQTT 
MQTT_BROKER = "localhost"
MQTT_PORTA = 1884
MQTT_TOPIC = "checkbox"

# Inicia o cliente MQTT (Publisher)
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) 
mqtt_client.connect(MQTT_BROKER, MQTT_PORTA, 60)
mqtt_client.loop_start()

# Cria objeto JID e cliente XMPP
jid = xmpp.JID(JID)
client = xmpp.Client(jid.getDomain(), debug=[])

# Conecta ao servidor (TCP)
print("[INFO] Conectando ao servidor XMPP...")
if not client.connect((SERVER, PORT)):
    print("[ERRO] Falha na conexão. Verifique se o Ejabberd está rodando.")
    exit(1)
print("[OK] Conectado ao servidor XMPP.")

# Autentica o usuário
if not client.auth(jid.getNode(), PASSWORD, resource='xmpppy'):
    print("[ERRO] Falha na autenticação. Verifique usuário e senha.")
    exit(1)
print("[OK] Autenticação XMPP bem-sucedida!")

# Envia presença inicial
client.sendInitPresence()
print("[OK] Presença enviada. Cliente XMPP")

# Callback para receber mensagens XMPP
def message_callback(conn, message):
    # Obtém o corpo da mensagem e o JID do remetente
    corpo_mensagem = message.getBody() 
    remetente = message.getFrom() 
    
    if corpo_mensagem: 
        print(f"\n[XMPP] Mensagem recebida de {remetente}: {corpo_mensagem}")
        
        # 1. Lógica XMPP: Resposta de confirmação (Comunicação Bidirecional)
        resposta_chat = f"🤖 Recebido. Comando XMPP/MQTT em processamento."
        msg_resposta = xmpp.Message(remetente, resposta_chat)
        msg_resposta.setType('chat')
        conn.send(msg_resposta)

        # Publicação do Comando (Ponte para IoT)
        comando = None
        
        # Limpa espaços em branco e verifica se é um comando (ATIVAR/DESATIVAR)
        comando_limpo = corpo_mensagem.upper().strip() 
        
        if "ATIVAR" == comando_limpo:
            comando = "ATIVAR"
        elif "DESATIVAR" == comando_limpo:
            comando = "DESATIVAR"
            
        if comando:
            # Publica o comando no Broker Mosquitto
            mqtt_client.publish(MQTT_TOPIC, comando)
            print(f"[MQTT] Publicado comando: {comando} no tópico {MQTT_TOPIC}")
        else:
            print(f"[XMPP] Nenhuma palavra-chave (ATIVAR/DESATIVAR) encontrada no corpo da mensagem: '{corpo_mensagem}'.")
            
client.RegisterHandler('message', message_callback)

# Mantém o cliente online
print(f"[INFO] Aguardando mensagens...")
while True:
    try:
        client.Process(1)
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[INFO] Desconectando Cliente XMPP e MQTT...")
        client.disconnect()
        mqtt_client.loop_stop()
        break
