import webbrowser
import hashlib
import json
import time
import os

#Funções auxiliares
def limpar_terminal():
    time.sleep(0.8)
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_caminho_arquivo(caminho_relativo_arquivo:str):
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(caminho_script,caminho_relativo_arquivo)
    caminho = os.path.normpath(caminho_completo)
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"ERRO: O CAMINHO '{caminho}' NÃO FOI ENCONTRADO.")
    return caminho

def carregar_dados(caminho_relativo_arquivo:str):
    caminho_arquivo = obter_caminho_arquivo(caminho_relativo_arquivo)
    try:
        with open(caminho_arquivo, "r", encoding="utf-8",) as arquivo:
            dados = json.load(arquivo)
        return dados
    except json.JSONDecodeError:
        print(f"ERRO: ARQUIVO '{caminho_arquivo}' CORROMPIDO OU VAZIO")
        return None
    except FileNotFoundError:
        print(f"ERRO: ARQUIVO '{caminho_arquivo}' NÃO ENCONTRADO")
        return None
    except Exception as e:
        print(f"OCORREU UM ERRO INESPERADO AO CARREGAR O ARQUIVO '{caminho_arquivo}': {e}")
        return None
    
def salvar_dados(dados: dict, caminho_relativo_arquivo:str):
    caminho_arquivo = obter_caminho_arquivo(caminho_relativo_arquivo)
    try:
        with open(caminho_arquivo, "w", encoding="utf-8",) as arquivo:
            json.dump(dados, arquivo, indent=4,ensure_ascii=False)
    except Exception as e:
        print(f"OCORREU UM ERRO INESPERADO AO SALVAR O ARQUIVO '{caminho_arquivo}': {e}")

def obter_entrada(mensagem: str):
    return input(mensagem).strip()  # Remove espaços extras

def gerar_hash_senha(senha: str):
    while len(senha) < 6:
        senha = obter_entrada("A SENHA DEVE TER 6 DÍGITOS \nSENHA: ")
    return hashlib.sha256(senha.encode()).hexdigest()

def confirmar_acao(mensagem: str):
    print(mensagem)
    while True:
        try:
            escolha = int(input(" [1] SIM \n [2] NÃO \n ESCOLHA UMA OPÇÃO: "))
            if escolha == 1:
                return True
            elif escolha == 2:
                return False
            else:
                print("OPÇÃO INVÁLIDA. DIGITE 1 PARA SIM ou 2 PARA NÃO.")
        except ValueError:
            print("ENTRADA INVÁLIDA. DIGITE UM NÚMERO INTEIRO.")

# Funções de Autenticação
def autenticar_usuario(nome: str, senha_hash: str,usuarios:list):
    for usuario in usuarios:
        if usuario["nome"] == nome and usuario["senha"] == senha_hash:
            return True
    else:return False

def login():
    usuarios = carregar_dados("json/usuarios.json")
    if not usuarios:
        return None
    nome = obter_entrada("NOME: ")
    senha = obter_entrada("SENHA: ")
    senha_hash = gerar_hash_senha(senha)
    if autenticar_usuario(nome, senha_hash, usuarios):
        return nome
    else:
        print("NOME OU SENHA INCORRETOS")
        return None

def excluir_usuario(nome:str):
    usuarios = carregar_dados("json/usuarios.json")
    senha = obter_entrada("SENHA :")
    hash_senha = gerar_hash_senha(senha)
    if not autenticar_usuario(nome, hash_senha, usuarios):
        print("Senha incorreta.")
        return
    if confirmar_acao("EXCLUIR CONTA ?.ESSA AÇÃO NÃO PODE SER DESFEITA"):
        for i, usuario in enumerate(usuarios):
            if usuario["nome"] == nome:
                del usuarios[i]
                salvar_dados(usuarios, "json/usuarios.json")
                print("CONTA EXCLUIDA COM SUCESSO")
                return
    else:print("EXCLUSÃO CANCELADA")

def alterar_senha(nome:str):
    usuarios = carregar_dados("json/usuarios.json")
    if confirmar_acao("TROCAR SENHA"):
        senha = obter_entrada("SENHA : ")
        hash_senha = gerar_hash_senha(senha)
        if not autenticar_usuario(nome,hash_senha,usuarios):
            print("SENHA INCORRETA")
            return
        nova_senha = obter_entrada("NOVA SENHA: ")
        confirmar_nova_senha = obter_entrada("CONFIRMAR NOVA SENHA: ")
        if nova_senha != confirmar_nova_senha:
            print("As novas senhas não coincidem.")
            return
        nova_senha_hash = gerar_hash_senha(nova_senha)
        for usuario in usuarios:
            if usuario["nome"] == nome:
                usuario["senha"] = nova_senha_hash
                salvar_dados(usuarios, "json/usuarios.json")
                print("SENHA ALTERADA COM SUCESSO.")
                return
        
def adicionar_usuario():
    usuarios = carregar_dados("json/usuarios.json")
    nome = obter_entrada("NOME : ")
    for usuario in usuarios:
        if usuario["nome"] == nome:
            print("USUÁRIO JÁ EXISTE")
            return
    senha = obter_entrada("SENHA : ")
    hash_senha = gerar_hash_senha(senha)
    novo_usuario = {"nome": nome, "senha": hash_senha, "boletim": {}}
    usuarios.append(novo_usuario)
    salvar_dados(usuarios, "json/usuarios.json")
    print("USUÁRIO CADASTRADO COM SUCESSO")
    
#Funções do sistema
def exibir_menu(opcoes: list):
    limpar_terminal()
    print('=' * 80)  
    for i, opcao in enumerate(opcoes):
        print(f" {opcao}")  
    print('=' * 80)

    while True:
        try:
            escolha = int(input('ESCOLHA UMA OPÇÃO: '))
            if 1 <= escolha <= len(opcoes):
                return escolha
            else:
                print(f'OPÇÃO INVÁLIDA. DIGITE UM NÚMERO ENTRE 1 E {len(opcoes)}.')
        except ValueError:
            print("ENTRADA INVÁLIDA. DIGITE UM NÚMERO INTEIRO.")

def abrir_url(url):
    print("ABRINDO LINK")
    webbrowser.open(url)

def exibir_aula(nome_materia:str):
    limpar_terminal
    aulas = carregar_dados("json/materias.json")
    if nome_materia in aulas:
        for aula in aulas[nome_materia]:
            limpar_terminal()
            print("_____________________________________________________________________________________________")
            print(f"{aula["titulo"].upper()}\n{aula["conteudo"].upper()}")
            print("_____________________________________________________________________________________________")
            input("DIGITE QUALQUER TECLA PARA A PROXIMA PARTE")
            
def realizar_prova(nome_materia:str,nome:str ):
    limpar_terminal()
    respostas = []
    provas = carregar_dados("json/provas.json")
    usuarios = carregar_dados("json/usuarios.json")
    acertos = 0
    nota_final = 0
    
    questoes = None  
    prova:dict
    for prova in provas:
        if nome_materia in prova:
            questoes = prova.get(nome_materia)  
            break
   
    if not questoes:
        print("PROVA INDISPONIVEL")
        return
    
    usuario_id = None  
    for usuario in usuarios:
        if usuario["nome"] == nome:  
            usuario_id = usuario
            break  
    
    usuario_id:dict
    if nome_materia in usuario_id.get("boletim"):
        print("VOCÊ JÁ REALIZOU ESTA PROVA.")
        return

    print(f"====================== PROVA DE {nome_materia.upper()} ======================")
    for i, questao in enumerate(questoes):
        print(f"\nQUESTÃO {i+1}:\n{questao['pergunta']}")
        resposta = input("RESPOSTA: ").lower()
        respostas.append(resposta)
        if resposta == questao["correta"]:
            acertos += 1

    if len(questoes) > 0:
        nota_final = (acertos / len(questoes)) * 10
        print(f"\nRESULTADO FINAL: Você acertou {acertos} de {len(questoes)} questões. Nota: {nota_final:.2f}")

    if usuario_id:
        usuario_id["boletim"][nome_materia]= nota_final  
        salvar_dados(usuarios,"json/usuarios.json")  
        print("NOTA SALVA NO BOLETIM.")
   
def exibir_boletim(nome: str):
    limpar_terminal()
    dados = carregar_dados("json/usuarios.json")
    id_usuario = None
    for usuario in dados:
        if usuario["nome"] == nome:
            id_usuario = usuario
            break

    if  "boletim" in id_usuario:
        print(f"====================== BOLETIM DE {nome.upper()} ======================")
        boletim = id_usuario["boletim"]
        if boletim:
            for materia, nota in boletim.items():
                print(f"{materia } : {nota:.2f}")
        else:print("AS NOTAS DAS PROVAS REALIZADAS APARECERÃO AQUI")
    input("DIFITE QUALQUER TECLA PARA VOLTAR")


fechar = False
while not fechar:
    #Menu principal
    opcao_principal = exibir_menu(["[1] CADASTRO","[2] LOGIN","[3] FECHAR"])

    if opcao_principal == 1:
        adicionar_usuario()

    elif opcao_principal == 2:
        nome = login()
        if nome:
            sair = False

            while not sair:
             #Menu do usuário
                opcao_usuario = exibir_menu(["[1] MATERIAS","[2] MATERIAL COMPLEMENTAR","[3] PROVAS","[4] BOLLETIM","[5] PERFIL","[6] SAIR"])
                
                if opcao_usuario == 1:
                    voltar_usuario = False
                    while not voltar_usuario:
                        #Menu materias/aulas
                        opcao_materia = exibir_menu(["[1] LOGICA DE PROGRAMAÇÃO","[2] TECNOLOGIA DA COMUNICAÇÃO E INFORMAÇÃO","[3] SEGURANÇA DIGITAL","[4] VOLTAR"])
                        if opcao_materia == 1:
                            exibir_aula("lógica de programação")    

                        elif opcao_materia == 2:
                            exibir_aula("tecnologia da informação e comunicação")
 
                        elif opcao_materia == 3:
                            exibir_aula("segurança digital")
                        
                        elif opcao_materia == 4:
                            voltar_usuario = True                               

                elif opcao_usuario == 2:
                    voltar_usuario = False
                    while not voltar_usuario:
                        #Menu videos
                        opcao_video = exibir_menu(["[1] VIDEO 1","[2] VIDEO 2","[3] VIDEO 3","[4] VIDEO 4","[5] VOLTAR"])
                        if opcao_video == 1:
                            abrir_url("https://www.youtube.com/watch?v=VQRLujxTm3c")
                        elif opcao_video == 2:
                            abrir_url("https://www.youtube.com/watch?v=VQRLujxTm3c")
                        elif opcao_video == 3:
                            abrir_url("https://www.youtube.com/watch?v=VQRLujxTm3c")
                        elif opcao_video == 4:
                            abrir_url("https://www.youtube.com/watch?v=VQRLujxTm3c")
                        
                        elif opcao_video == 5:
                            voltar_usuario = True
                
                elif opcao_usuario == 3:
                    voltar_usuario = False
                    while not voltar_usuario:
                        #Menu provas
                        opcao_prova = exibir_menu(["[1] LÓGICA DE PROGRAMAÇÃO","[2] TECNOLOGIA DA COMUNICAÇÃO E INFORMAÇÃO","[3] SEGURANÇA DIGITAL","[4] VOLTAR"])
                        
                        if opcao_prova == 1:
                            realizar_prova("lógica de programação",nome)
                        
                        elif opcao_prova == 2:
                            realizar_prova("tecnologia da informação e comunicação",nome)
                        
                        elif opcao_prova == 3:
                            realizar_prova("segurança digital",nome)
                        elif opcao_prova == 4:
                            voltar_usuario = True

                elif opcao_usuario == 4:
                    exibir_boletim(nome)
                
                elif opcao_usuario == 5:
                    voltar_usuario = False
                    while not voltar_usuario:
                     #Menu perfil
                        opcao_perfil = exibir_menu(["[1] TROCAR SENHA","[2] EXCLUIR CONTA","[3] VOLTAR"])
                        if opcao_perfil == 1:
                            alterar_senha(nome)
                        elif opcao_perfil == 2:
                            excluir_usuario(nome)
                            sair = True
                            voltar_usuario = True
                        elif opcao_perfil == 3:
                            voltar_usuario = True

                elif opcao_perfil == 6:
                    voltar_usuario = True

    elif opcao_principal == 3:
        fechar = True
        