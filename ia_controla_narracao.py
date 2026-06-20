from smolagents import CodeAgent, InferenceClientModel, tool
#from smolagents import TransformersModel 
import os, time

#os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


token = "ADD_TOKEN"

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
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    )

@tool
#Aqui o agente recebe o personagem que for detectado no palco
def verificar_palco() -> str:
    """
    Verifica quais cientistas foram detectados no palco atualmente.
    O retorno pode ser um único cientista ou vários separados por vírgula, ex: 'Isaac Newton, Albert Einstein, Ada Lovelace'.
    
    Returns:
        str: Uma lista ou nome dos cientistas presentes no suporte.
    """
    #usando o arquivo como um mock do palco
    with open("palco.txt","r",encoding="utf-8") as arquivo:
        personagem = arquivo.read().strip()
        
    print("Verificando palco...")
    #print(f"Cientista detectado {personagem}")
    
    return personagem


@tool
def mover_elemento(elemento: str, angulo: int) -> str:
    """
    Move um ou mais elementos do cenário.
    Elementos disponíveis: prisma, foguete, lua, computador
    
    Args:
        elemento: O nome do objeto/cenário que deve ser movido (ex: 'prisma').
        angulo: O ângulo de rotação para o servo motor (de 0 a 180 graus).
    Returns:
        str: Confirmação do movimento do elemento.
    """
    comando = f"MOVER_SERVO:{elemento}:{angulo}"
    print(f"[PSEUDOCOMANDO] {comando}")

    ## Aqui seria a integraçao com o codigo da Julia

    return f"Servo do(a) {elemento} movido para {angulo} graus"


@tool
def acender_led(cor: str) -> str:
    """
    Envia um comando para acender o LED específico do cenário.
    Se houver 2 ou mais cientistas, acende o LED  'amarelo' (indicando crossover).
    Cores disponíveis: vermelho, amarelo, verde, azul
    
    Args:
        cor: A cor desejada para o LED (exemplos: 'branca', 'vermelha', 'azul').
    Returns:
        str: Confirmação do comando enviado ao hardware.
    """
    #print(f"[COMANDO HARDWARE] LED alterado para a cor: {cor}")
    comando = f"Acende LED da cor:{cor}"
    print(f"[PSEUDOCOMANDO] {comando}")
    return f"Acende LED da cor {cor}"


@tool
def narrar(texto: str) -> str:
    """Narra o texto gerado pela IA sobre o cientista
    Controla o arquivo narracao.txt mudando para 'True' enquanto fala e 'False' ao terminar.
    
    Args:
        texto: O texto/história que o narrador digital deve falar.
    """
    with open("narracao.txt", "w", encoding="utf-8") as f:
        f.write("True")
    print("\n [NARRADOR] Audio ativado")
    print(f'Narrando: "{texto}"')
    time.sleep(5)
    with open("narracao.txt", "w", encoding="utf-8") as f:
        f.write("False")
    print(" [NARRADOR] Audio Concluído")
    return "Narração executada com sucesso"

#Verificar se eu preciso passar o nome das tools mesmo ou nao
agent = CodeAgent(
    tools = [verificar_palco,mover_elemento,acender_led,narrar],
    model = modelo
)

prompt = """
Você é o diretor de um teatro científico automatizado. 
            
Loop:
1. Cheque se há um ou mais personagens no palco, com verificar_palco(). O retorno pode ser um único cientista ou vários separados por vírgula, ex: 'Isaac Newton, Albert Einstein, Ada Lovelace'.
2. Se o retorno for um ou mais cientistas válidos e se for diferente do(s) último(s) cientista(s) no palco:
    2.1. Printe qual(is) cientista(s) está(ão) no palco e ative as ferramentas mover_elemento() e acender_led() adequadas para cada um deles.
    2.2. Crie uma cena,em inglês, seguindo essas regras:
        * Se for apenas 1 cientista: Crie uma narrativa curta, com linguagem infantil apresentando o cientista e seu experimento.
        * Se forem 2 ou mais cientistas: Crie um diálogo curto, de 4 falas, com linguagem infantil entre eles (que pode ou não envolver os elementos do cenário).
        
    2.3 Passe essa narrativa, ou diálogo, como argumento para a ferramenta narrar().
3. Aguarde alguma mudança no palco.

Execute esse loop continuamente. 

"""    
agent.run(prompt)
            