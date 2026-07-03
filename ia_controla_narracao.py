import json, os, time
from smolagents import CodeAgent, InferenceClientModel, tool
import arduino

'''
TO-DO
- ajeitar as vozes que nao estao sendo salvas na memoria ao reiniciar o teatro
'''

SERVOS = {"prisma": 1, "foguete": 2, "lua": 3}
EFEITOS_VALIDOS = ["apagar", "branco", "fogo", "espectro", "dispersao", "dados", "calculo", "decolagem", "respirar"]

#os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

ultimo_estado_palco = ""
ultima_historia = ""
teatro_ligado = True

token = "SEU TOKEN"

'''
modelo = TransformersModel(
    model_id="Qwen/Qwen2.5-1.5B-Instruct",
    #host="http://localhost:11434"
    device_map="auto"
)

modelo = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:1.5b"
)

'''
modelo = InferenceClientModel(
    token=token,
    #model_id = "Qwen/Qwen2.5-7B-Instruct"
    model_id = "meta-llama/Llama-3.1-8B-Instruct"
    )

@tool
#Aqui o agente recebe o personagem que for detectado no palco
def verificar_palco() -> str:
    """
    Verifica quais cientistas foram detectados no palco.
    Se os cientistas forem os mesmos da última verificação, retorna 'Sem mudanças'.
    Se houver novos cientistas, retorna o nome deles para que uma nova cena seja criada.
    O retorno pode ser um único cientista, vários separados por vírgula (ex: 'Isaac Newton, Albert Einstein'), ou 'Sem mudanças'.
    
    Returns:
        str: Uma lista ou nome dos cientistas presentes no suporte.
    """
    global ultimo_estado_palco, teatro_ligado
    
    if not teatro_ligado:
        import sys
        sys.exit()
    
    #Se a interface do audio estiver tocando, não faz nada
    if os.path.exists("narracao.txt"):
        with open("narracao.txt", "r", encoding="utf-8") as f:
            if f.read().strip() == "True":
                print("Narrando.")
                return "Sem mudanças"
            
    if not os.path.exists("palco.txt"):
        return "Sem mudanças"
            
    #usando o arquivo como um mock do palco
    with open("palco.txt","r",encoding="utf-8") as arquivo:
        personagens_atuais = arquivo.read().strip()
        
    if personagens_atuais and personagens_atuais != ultimo_estado_palco:
        print(f"Mudança detectada! Novos personagens: {personagens_atuais}")
        ultimo_estado_palco = personagens_atuais
        return personagens_atuais
    else:
        print("Sem mudanças no palco.")
        # Se não houver ninguém ou for o mesmo personagem, informa o agente.
        return "Sem mudanças"

@tool
def mover_elemento(elemento: str, acao: str) -> str:
    """
    Move um elemento do cenario, subindo ou descendo ele.
    Alguns elementos disponiveis e seus servos:
    Servo 1 - Lua 
    Servo 2 - Foguete
    Servo 3 - Prisma
    Para os outros personagens deixe os servos parados.
    Acoes disponiveis: 'subir' (mostra o elemento) ou 'descer' (esconde o elemento) ou 'mover' (varia a posicao do servo).

    Quando um cientista entra em cena, suba o elemento dele.
    Quando um cientista sai de cena, desca o elemento dele antes de subir o do proximo.
    
    Args:
        elemento: O nome do objeto/cenário que deve ser movido (ex: 'prisma').
        acao: 'subir' ou 'descer' ou 'mover'.
    Returns:
        str: Confirmação do movimento do elemento.
    """

    numero = SERVOS[elemento]
    comando = f"servo {numero} {acao}"
    print(f" [DEBUG SERVO] IA mandando: {comando}")
    arduino.enviar(comando)
    return f"Servo do(a) {elemento} executou: {acao}"

    ##comando = f"MOVER_SERVO:{elemento}:{angulo}"
    ##print(f"[PSEUDOCOMANDO] {comando}")

    ## Aqui seria a integraçao com o codigo da Julia

    ##return f"Servo do(a) {elemento} movido para {angulo} graus"


@tool
def acender_led(efeito: str) -> str:
    """
    Muda o efeito de luz da fita de LED do cenario.
    Efeitos disponiveis: apagar, branco, fogo, espectro, dispersao, dados, calculo, decolagem, respirar.

    Para todo personagem escolha o efeito que combina com ele
    (exemplo: 'dispersao' para Newton e a luz/prisma, 'decolagem' para foguetes, 'dados' ou 'calculo' para computacao). Ou seja, associe cada fenômeno dos leds aos seus respectivos personagens
    
    Args:
        efeito: O nome do efeito de luz (ex: 'espectro', 'dispersao', 'fogo').
    Returns:
        str: Confirmação do comando enviado ao hardware.
    """

    if efeito not in EFEITOS_VALIDOS:
        return f"Efeito '{efeito}' invalido. Use um destes: {EFEITOS_VALIDOS}"
    
    comando = f"led {efeito} 40"
    arduino.enviar(comando)
    return f"Efeito de LED alterado para: {efeito}"

    #print(f"[COMANDO HARDWARE] LED alterado para a cor: {cor}")
    #comando = f"Acende LED da cor:{cor}"
    #print(f"[PSEUDOCOMANDO] {comando}")
    #return f"Acende LED da cor {cor}"


@tool
def narrar(historia: list) -> str:
    """
    Aguarda pacientemente até que a interface física e o áudio terminem de rodar.
    Monitora o arquivo narracao.txt.
    
    Args:
        historia: O texto/história enviado para controle do fluxo.
    """
    global ultima_historia
    global ultimo_estado_palco
    
    texto_consolidado = (
        f"{ultimo_estado_palco}-"
        + "".join([fala.get("texto", "") for fala in historia])
    )

    if texto_consolidado == ultima_historia:
        print("[NARRADOR] Esta cena exata com este(s) personagem(ns) já foi narrada. Ignorando repetição.")
        return "Ignorado"

    print(
        "\n[IA] Aguardando a interface iniciar e concluir a reprodução do áudio..."
    )
    # Dá uma pequena janela de tempo para a interface gráfica ler o historia.json e setar como "True"
    time.sleep(2)

    # Loop de espera real: enquanto o arquivo indicar que a interface está narrando, a IA fica travada aqui
    timeout_seguranca = 0
    while os.path.exists("narracao.txt"):
        with open("narracao.txt", "r", encoding="utf-8") as f:
            estado = f.read().strip()
        
        if estado == "False":
            break
            
        time.sleep(0.5)
        timeout_seguranca += 0.5
        if timeout_seguranca > 60: # Evita travar o agente para sempre se houver um bug no som
            print("[IA] Timeout de segurança atingido.")
            break
            
    print("[IA] Áudio concluído na interface. Liberando agente para nova checagem.")
    
    ultima_historia = texto_consolidado
    return "Narração concluída com sucesso"


@tool
def salvar_historia(historia: list) -> str:
    """
    Salva a história gerada pela IA em um arquivo JSON.

    Args:
        historia: Lista de dicionários no formato:
        [
            {
                "personagem": "Nome",
                "texto": "Fala"
            }
        ]
    """

    with open("historia.json", "w", encoding="utf-8") as arquivo:
        json.dump(
            historia,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print("[HISTORIA] Arquivo salvo com sucesso.")

    return "História salva com sucesso."


def carregar_informacoes_teatro():
    caminho_arquivo = "memoria_teatro.json"
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return None
            


tools = [verificar_palco, mover_elemento, acender_led, narrar, salvar_historia]

#Verificar se eu preciso passar o nome das tools mesmo ou nao
agent = CodeAgent(
    tools = tools,
    model = modelo
)
agent.authorized_imports.extend(["random", "time"])

prompt = """
Você é o diretor e o roteirista criativo do teatro automatizado. 
Sua missão é monitorar o palco por tempo indeterminado e dar vida aos personagens que aparecerem através de roteiros teatrais lúdicos.
Fique de olho no palco constantemente. 
A cada poucos segundos, utilize a ferramenta de verificação para saber quem está em cena. 
Se o retorno for 'Sem mudanças', simplesmente aguarde um momento usando uma pausa e verifique novamente, sem realizar nenhuma outra ação.

Quando novos personagens entrarem em cena, assuma o controle físico do teatro: 
mova os elementos cenográficos correspondentes e mude a cor da iluminação em LED para cada um deles. 

Exerça seu papel de roteirista apenas quando novos personagens forem detectados, crie uma lista 'historia' totalmente nova e limpa, sem usar memórias ou falas de cenas anteriores.

Gere um roteiro, inédito e criativo, em ingles.
Se houver mais de um personagem em cena, crie um diálogo dinâmico onde eles interagem entre si, mantendo o tema
Não utilize lógica de programação para definir as falas; em vez disso, use sua capacidade de geração de texto para criar um conteúdo original e único para cada rodada.

Formate o resultado como uma lista de dicionários com as chaves "personagem" (nome exato) e "texto" (apenas a fala limpa). 
Envie essa lista ('historia') como argumento para salvar_historia(historia) e narrar(historia), faça uma pausa de alguns segundos e reinicie o loop. 
Mantenha-se vigiando o palco para sempre.

"""

def iniciar_loop_ia():
    config = carregar_informacoes_teatro()
    #Valores padrão
    clima = "neutro"
    tema = "ciência"
    personagens = "cientistas gerais"

    if config:
        if "cenario" in config:
            clima = config["cenario"].get("clima", "neutro")
            tema = config["cenario"].get("tema", "ciência")
        if "personagens" in config:
            personagens = ", ".join(config["personagens"].keys())

    prompt_dinamico = f"""
    {prompt}

    DIRETRIZES ADICIONAIS DO DIRETOR:
    - O clima da história deve ser: {clima}.
    - O tema geral do teatro deve ser focado em: {tema}.
    - Os personagens que podem aparecer no palco são: {personagens}. 
    
    Por favor, incorpore o tema '{tema}' e o clima '{clima}' em todos os roteiros gerados.
    """
    agent.run(prompt_dinamico)
            
