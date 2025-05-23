import webbrowser
import datetime
import hashlib
import bcrypt
import json
import time
import os
import re 

#Funções auxiliares
def limpar_terminal():
    time.sleep(0.8)
    os.system('cls' if os.name == 'nt' else 'clear')

def abrir_url(url):
    print("ABRINDO LINK")
    webbrowser.open(url)
    registrar_log("ACESSO_MATERIAL_COMPLEMENTAR",nome_hash,f"URL: {url}")

def obter_caminho_arquivo(caminho_relativo_arquivo:str):
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(caminho_script,caminho_relativo_arquivo)
    caminho = os.path.normpath(caminho_completo)
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"ERRO: O CAMINHO '{caminho}' NÃO FOI ENCONTRADO.")
    return caminho

def carregar_arquivo(caminho_relativo_arquivo:str):
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
    
def salvar_arquivo(dados: dict, caminho_relativo_arquivo:str):
    caminho_arquivo = obter_caminho_arquivo(caminho_relativo_arquivo)
    try:
        with open(caminho_arquivo, "w", encoding="utf-8",) as arquivo:
            json.dump(dados, arquivo, indent=4,ensure_ascii=False)
    except Exception as e:
        print(f"OCORREU UM ERRO INESPERADO AO SALVAR O ARQUIVO '{caminho_arquivo}': {e}")

def obter_entrada(mensagem: str):
    return input(mensagem).strip()  # Remove espaços extras

def gerar_hash_senha(senha: str):
    while len(senha)<6:
        senha = obter_entrada("A SENHA DEVE TER NO MINIMO 6 DIGITOS\nSENHA :")
    salt = bcrypt.gensalt(12)
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hash_senha.decode("utf-8")   
   
def gerar_hash_nome(nome):
    return hashlib.sha256(nome.encode()).hexdigest()

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

def registrar_log(tipo_evento, usuario_hash, descricao):
    """Registra eventos de segurança em um arquivo JSON como uma lista de dicionários."""
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log = {
        "data e hora": data_hora,
        "tipo_evento": tipo_evento,
        "descricao": descricao,
        "usuario_hash": usuario_hash
    }

    try:
        logs = carregar_arquivo("registro_logs.json")
        logs.append(log)
        salvar_arquivo(logs, "registro_logs.json")
    except Exception as e:
        print(f"Erro ao registrar log (JSON): {e}")

# Funções de Autenticação
def autenticar_usuario(nome_hash: str, senha: str,usuarios:list):
    for usuario in usuarios:
        if usuario["nome"] == nome_hash :
            if bcrypt.checkpw(senha.encode("utf-8"), usuario["senha"].encode('utf-8')):
                return True
            else:return False 
    else:return False#usuario nao encontrado

def validar_email(email):
    # Regex simples para validar formato de e-mail (pode ser mais robusto)
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def login():
    usuarios = carregar_arquivo("usuarios.json")
    if not usuarios:
        return None
    nome = obter_entrada("NOME: ")
    nome_hash = gerar_hash_nome(nome)
    senha = obter_entrada("SENHA: ")
    if autenticar_usuario(nome_hash, senha, usuarios):
        registrar_log("AUTENTICACAO_ENTRADA", nome_hash, "Login bem-sucedido")
        return nome_hash
    else:
        registrar_log("AUTENTICACAO_FALHA",nome_hash,"Credenciais inválidas")
        print("NOME OU SENHA INCORRETOS")
        return None

def excluir_usuario(nome_hash:str):
    usuarios = carregar_arquivo("usuarios.json")
    senha = obter_entrada("SENHA :")
    if not autenticar_usuario(nome_hash,senha, usuarios):
        registrar_log("CONTA_EXCLUIDA_FALHA", nome_hash, "Credenciais inválidas")
        print("Senha incorreta.")
        return
    if confirmar_acao("EXCLUIR CONTA ?.ESSA AÇÃO NÃO PODE SER DESFEITA"):
        for i, usuario in enumerate(usuarios):
            if usuario["nome"] == nome_hash:
                del usuarios[i]
                salvar_arquivo(usuarios, "usuarios.json")
                registrar_log("CONTA_EXCLUIDA", nome_hash, "Conta de usuário excluída permanentemente")
                print("CONTA EXCLUIDA COM SUCESSO")
                return  True , True
                           
    else:print("EXCLUSÃO CANCELADA")

def alterar_senha(nome_hash:str):
    usuarios = carregar_arquivo("usuarios.json")
    if confirmar_acao("TROCAR SENHA"):
        senha = obter_entrada("SENHA : ")
        if not autenticar_usuario(nome_hash,senha,usuarios) or senha is None:
            registrar_log("SENHA_ALTERADA_FALHA",nome_hash,"Falha ao autenticar usuario")
            print("SENHA INCORRETA")
            return
        nova_senha = obter_entrada("NOVA SENHA: ")
        confirmar_nova_senha = obter_entrada("CONFIRMAR NOVA SENHA: ")
        if nova_senha != confirmar_nova_senha:
            print("AS SENHAS SÃO DIERENTES.")
            registrar_log("SENHA_ALTERADA_FALHA",nome_hash,"Erro ao confirmar senha")
            return
        nova_senha_hash = gerar_hash_senha(nova_senha)
        for usuario in usuarios:
            if usuario["nome"] == nome_hash:
                usuario["senha"] = nova_senha_hash
                salvar_arquivo(usuarios, "usuarios.json")
                registrar_log("SENHA_ALTERADA",nome_hash,"Senha alterada com sucesso")
                print("SENHA ALTERADA COM SUCESSO.")
                return
        
def alterar_email(nome_hash: str):
    
    usuarios = carregar_arquivo("usuarios.json")
    if not usuarios:
        print("Nenhum usuário encontrado.")
        return

    usuario_encontrado = None
    for usuario in usuarios:
        if usuario["nome"] == nome_hash:
            usuario_encontrado = usuario
            break

    if not usuario_encontrado:
        print("Usuário não encontrado.")
        return

    print(f"\nSeu e-mail atual é: {usuario_encontrado.get('email', 'Não definido')}")
    while True:
        novo_email = input("Digite o novo e-mail (ou 'cancelar' para voltar): ").strip()
        if novo_email.lower() == 'cancelar':
            print("Alteração de e-mail cancelada.")
            return

        if not validar_email(novo_email):
            print("Formato de e-mail inválido. Por favor, digite um e-mail válido.")
            continue

      
        email_ja_existe = False
        for usuario in usuarios:
            if usuario["nome"] != nome_hash and usuario.get("email") == novo_email:
                email_ja_existe = True
                break
        
        if email_ja_existe:
            print("Este e-mail já está em uso por outro usuário. Por favor, escolha outro.")
        else:
            usuario_encontrado["email"] = novo_email
            if salvar_arquivo(usuarios, "usuarios.json"):
                print("E-mail alterado com sucesso!")
                registrar_log("EMAIL_ALTERADO", nome_hash, f"E-mail alterado para: {novo_email}")
            else:
                print("Ocorreu um erro ao salvar o novo e-mail.")
            break

def adicionar_usuario():
    limpar_terminal()
    url= "https://github.com/Edu220011/PIM-2025---Eduardo-Antonio-de-Almeida-Oliveira/blob/916fb09ffea26eeb98ed5c4a73d92b304f5e96ae/PLATAFORMA%20DE%20EDUCA%C3%87%C3%83O%20DIGITAL%20BEGH/POL%C3%8DTICA%20DE%20PRIVACIDADE%20E%20PROTE%C3%87%C3%83O%20DE%20DADOS%20PESSOAIS%20DA%20PED-.pdf"
    confirmar_acao(f"lI E CONCORDO COM AS POLITICAS DE SEGURANÇA [{url}]\nPARA ABRIR O LINK PRECIONE CTRL E CLIQUE COM O BOTÃO DIREITO DO MOUSE \nOU SE O TERMINAL NÃO PERMITIR COPIE O COLE O LINK NO SEU NAVEGADOR")
    usuarios = carregar_arquivo("usuarios.json")
    nome = obter_entrada("NOME :")
    while len(nome) < 4:
        nome = input("NOME DEVE TER NO MINIMO 4 DIGITOS\nNOME:")
    nome_hash = gerar_hash_nome(nome)
    for usuario in usuarios:
        if usuario["nome"] == nome_hash:
            print("USUÁRIO JÁ EXISTE")
            return
    
    email = obter_entrada("EMAIL : ")
    while validar_email(email) is None:
        email = obter_entrada("DIGITE UM EMAIL VÁLIDO\nEMAIL : ")
    senha = obter_entrada("SENHA : ")
    senha_hash = gerar_hash_senha(senha)
    idade = obter_entrada("IDADE : ")
    novo_usuario = {"nome": nome_hash,"idade":idade, "email":email,"senha": senha_hash, "boletim": {}}
    usuarios.append(novo_usuario)
    salvar_arquivo(usuarios, "usuarios.json")
    registrar_log("CONTA_CRIADA",nome_hash,"Novo usuário cadastrado")
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

def exibir_aula(nome_materia:str):
    limpar_terminal
    aulas = carregar_arquivo("materias.json")
    if nome_materia in aulas:
        for aula in aulas[nome_materia]:
            limpar_terminal()
            print("_____________________________________________________________________________________________")
            print(f"{aula["titulo"].upper()}\n{aula["conteudo"].upper()}")
            print("_____________________________________________________________________________________________")
            input("PRSSIONE ENTER")
    registrar_log("ACESSO_AULA",nome_hash,f"Usuário acessou conteúdo da aula: [{nome_materia}]")        

def realizar_prova(nome_materia:str,nome_hash:str ):
    limpar_terminal()
    respostas = []
    provas = carregar_arquivo("provas.json")
    usuarios = carregar_arquivo("usuarios.json")
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
        if usuario["nome"] == nome_hash  : 
            usuario_id = usuario
            break  
    
    usuario_id:dict
    if nome_materia in usuario_id.get("boletim"):
        print("VOCÊ JÁ REALIZOU ESTA PROVA.")
        return

    print(f"====================== PROVA DE {nome_materia.upper()} ======================")
    registrar_log("PROVA_INICIADA",nome_hash,f"Usuário iniciou prova de: [{nome_materia}]")
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
        salvar_arquivo(usuarios,"usuarios.json")
        registrar_log("PROVA_CONCLUIDA",nome_hash,f"Usuário concluiu prova de: [{nome_materia}]")
        registrar_log("NOTA_REGISTRADA",nome_hash,(f"Nota de prova de [{nome_materia}] registrada: {nota_final}"))  
        print("NOTA SALVA NO BOLETIM.")
    limpar_terminal()
   
def exibir_boletim(nome_hash: str):
    limpar_terminal()
    dados = carregar_arquivo("usuarios.json")
    id_usuario = None
    for usuario in dados:
        if usuario["nome"] == nome_hash:
            id_usuario = usuario
            break

    if  "boletim" in id_usuario:
        print(f"======================= BOLETIM ======================")
        boletim = id_usuario["boletim"]
        if boletim:
            for materia, nota in boletim.items():
                print(f"{materia } : {nota:.2f}")
        else:print("AS NOTAS DAS PROVAS REALIZADAS APARECERÃO AQUI")
    input("PRESIONE ENTER")
    registrar_log("BOLETIM_VISUALIZADO",nome_hash,"Usuário visualizou seu boletim de notas")

def limpar_logs_antigos():
    logs = carregar_arquivo("registro_logs.json")
    if not logs:
        return

    data_limite = datetime.datetime.now() - datetime.timedelta(days=180) # 6 meses
    logs_filtrados = []
    for log in logs:
        try:
            data_log_str = log.get("data e hora")
            if data_log_str:
                data_log = datetime.datetime.strptime(data_log_str, "%Y-%m-%d %H:%M:%S")
                if data_log >= data_limite:
                    logs_filtrados.append(log)
            else:
                logs_filtrados.append(log) # Manter logs sem data, embora seja uma anomalia
        except ValueError:
            logs_filtrados.append(log) # Manter logs com formato de data inválido, para investigação

    if len(logs) != len(logs_filtrados):
        salvar_arquivo("registro_logs.json", logs_filtrados)       
    
limpar_logs_antigos()
fechar = False
while not fechar:
    #Menu principal
    opcao_principal = exibir_menu(["[1] CADASTRO","[2] LOGIN","[3] ESQUECI MINHA SENHA","[4] FECHAR"])

    if opcao_principal == 1:
        adicionar_usuario()

    elif opcao_principal == 2:
        nome_hash = login()
        if nome_hash:
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
                        opcao_video = exibir_menu(["[1] VERIFICAÇÃO NO WINDOWS","[2] DELETANDO  ARQUIVOS TEMPORÁRIOS","[3] LIMPEZA DE DISCO","[4] VERIFICAÇÃO PELO CMD","[5] DEIXANDO O PC COM MAIS ARMAZENAMENTO","[6] VERIFICAÇÃO DE SEGURANÇA","[7] VOLTAR"])
                        if opcao_video == 1:
                            abrir_url("https://www.youtube.com/watch?v=Ng6yiGqGk6o")
                        elif opcao_video == 2:
                            abrir_url("https://www.youtube.com/watch?v=XjX1bAybYYY")
                        elif opcao_video == 3:
                            abrir_url("https://www.youtube.com/watch?v=sJ_MAMYRiVc")
                        elif opcao_video == 4:
                            abrir_url("https://www.youtube.com/watch?v=WLJJEHU4nGY")
                        elif opcao_video == 5:
                            abrir_url("https://www.youtube.com/watch?v=8isc7G2UNTc")
                        elif opcao_video == 6:
                            abrir_url("https://www.youtube.com/watch?v=2wVXoM85pgk")
                        elif opcao_video == 7:
                            voltar_usuario = True
                
                elif opcao_usuario == 3:
                    voltar_usuario = False
                    while not voltar_usuario:
                        #Menu provas
                        opcao_prova = exibir_menu(["[1] LÓGICA DE PROGRAMAÇÃO","[2] TECNOLOGIA DA COMUNICAÇÃO E INFORMAÇÃO","[3] SEGURANÇA DIGITAL","[4] VOLTAR"])
                        
                        if opcao_prova == 1:
                            realizar_prova("lógica de programação",nome_hash)
                        
                        elif opcao_prova == 2:
                            realizar_prova("tecnologia da informação e comunicação",nome_hash)
                        
                        elif opcao_prova == 3:
                            realizar_prova("segurança digital",nome_hash)
                        elif opcao_prova == 4:
                            voltar_usuario = True

                elif opcao_usuario == 4:
                    exibir_boletim(nome_hash)
                
                elif opcao_usuario == 5:
                    voltar_usuario = False
                    while not voltar_usuario:
                     #Menu perfil
                        opcao_perfil = exibir_menu(["[1] TROCAR SENHA","[2] TROCAR EMAIL","[3] EXCLUIR CONTA","[4] POLITICA DE SEGURANÇA","[5] VOLTAR"])
                        if opcao_perfil == 1:
                            alterar_senha(nome_hash)
                        elif opcao_perfil == 2:
                            alterar_email(nome_hash)
                        elif opcao_perfil == 3:
                            sair,valtar_usuario = excluir_usuario(nome_hash)
                        elif opcao_perfil == 4:
                            abrir_url("https://github.com/Edu220011/PIM-2025---Eduardo-Antonio-de-Almeida-Oliveira/blob/916fb09ffea26eeb98ed5c4a73d92b304f5e96ae/PLATAFORMA%20DE%20EDUCA%C3%87%C3%83O%20DIGITAL%20BEGH/POL%C3%8DTICA%20DE%20PRIVACIDADE%20E%20PROTE%C3%87%C3%83O%20DE%20DADOS%20PESSOAIS%20DA%20PED-.pdf")
                        elif opcao_perfil == 5:
                            voltar_usuario = True

                elif opcao_usuario == 6:
                    registrar_log("SESSAO_ENCERRADA", nome_hash,"Usuário fez logout")
                    sair = True
                    
    elif opcao_principal == 3:
        print("CONTATE O ADMIN 'EMAIL'")
    elif opcao_principal == 4:
        fechar = True
      