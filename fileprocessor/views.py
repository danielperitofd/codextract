# fileprocessor/views.py
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.utils.html import format_html
from zipfile import ZipFile
from django.conf import settings
import os
import datetime

# Função para listar hierarquia de arquivos e pastas, simulando o comando 'tree /F /A'
def gerar_hierarquia_pastas(diretorio_base):
    print(f"Caminho da pasta base: {diretorio_base}")
    
    if not os.path.exists(diretorio_base):
        print(f"A pasta {diretorio_base} não existe!")
        return ""

    estrutura = []
    estrutura.append(f"Pasta raiz: {os.path.basename(diretorio_base)}")
    
    # Usar os.walk para navegar por diretórios e arquivos
    for root, dirs, files in os.walk(diretorio_base):
        # Verificação para garantir que estamos dentro de um diretório válido
        print(f"Root atual: {root}")
        nivel = root.replace(diretorio_base, "").count(os.sep)
        
        # Indentação para mostrar a hierarquia
        indentacao = "│   " * nivel + "├── "
        estrutura.append(f"{indentacao}{os.path.basename(root)}/")
        
        # Adicionar arquivos dentro do diretório atual
        sub_indentacao = "│   " * (nivel + 1) + "├── "
        for f in files:
            estrutura.append(f"{sub_indentacao}{f}")
    
    return "\n".join(estrutura)

# Função para limpar espaçamentos e preservar indentação
def limpar_espacos_preservando_indentacao(conteudo):
    linhas = conteudo.splitlines()
    conteudo_limpo = []
    for linha in linhas:
        if linha.strip():
            # Preserva indentação original
            conteudo_limpo.append(linha)
    return "\n".join(conteudo_limpo)

# Função para upload de arquivos e criação de um arquivo ZIP
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import datetime

# Função para upload de arquivos e criação de um arquivo txt
def upload_file(request):
    if request.method == 'POST':
        # Obter os arquivos enviados
        uploaded_files = request.FILES.getlist('files')
        
        if uploaded_files:
            try:
                # Criar um nome único para o arquivo combinado
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"arquivos_combinados_{timestamp}.txt"
                fs = FileSystemStorage()
                output_path = os.path.join(fs.location, output_filename)

                # Criar o arquivo combinado
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    for uploaded_file in uploaded_files:
                        # Escrever o título do arquivo
                        file_title = f"Arquivo: {uploaded_file.name}"
                        output_file.write("=================================================\n")
                        output_file.write(f"{file_title}\n")
                        output_file.write("=================================================\n")
                        
                        # Escrever o conteúdo do arquivo
                        content = uploaded_file.read().decode('utf-8', errors='ignore')
                        content_cleaned = limpar_espacos_preservando_indentacao(content)
                        output_file.write(content_cleaned)
                        output_file.write("\n\n")
                
                # Retornar a resposta HTML com o conteúdo de sucesso e o link de download
                response_html = """
                    <html>
                    <head>
                        <link rel="stylesheet" type="text/css" href="/static/css/styles.css">
                    </head>
                    <body>
                        <div class="success-message">
                            Arquivos carregados e combinados com sucesso!
                        </div>
                        <a href="/media/{0}" class="download-btn" download>Baixar o arquivo combinado</a>
                    </body>
                    </html>
                """.format(output_filename)

                return HttpResponse(response_html)

            except Exception as e:
                return HttpResponse(f"Erro ao processar os arquivos: {str(e)}")
        
        # Caso nenhum arquivo tenha sido enviado
        return HttpResponse("Nenhum arquivo foi enviado.")
    
    # Renderizar o formulário para upload
    return render(request, 'fileprocessor/upload.html')

def processar_arquivos(request):
    # Configuração do sistema de arquivos
    fs = FileSystemStorage()
    
    # Garantir que a pasta 'media' exista
    if not os.path.exists(fs.location):
        os.makedirs(fs.location)

    # Listar os arquivos enviados
    arquivos = fs.listdir('')[1]  # Obtém apenas os arquivos
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo_saida = f'projeto_em_questao_{timestamp}.txt'
    caminho_arquivo_saida = os.path.join(fs.location, nome_arquivo_saida)

    try:
        # Salvar a estrutura de diretórios em um arquivo separado
        arquivo_estrutura_path = salvar_estrutura_em_arquivo(fs.location)

        # Criar o arquivo de saída com os arquivos processados
        with open(caminho_arquivo_saida, 'w', encoding='utf-8') as f_saida:
            # Escrever a hierarquia de arquivos (caso tenha sido gerado)
            if arquivo_estrutura_path:
                f_saida.write("HIERARQUIA DE ARQUIVOS E PASTAS:\n")
                f_saida.write("================================\n")
                f_saida.write(f"A hierarquia de arquivos foi salva em: {arquivo_estrutura_path}\n\n")

            # Processar cada arquivo individualmente
            for arquivo in arquivos:
                caminho_arquivo = os.path.join(fs.location, arquivo)
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f_entrada:
                        conteudo = f_entrada.read()
                        conteudo_limpo = limpar_espacos_preservando_indentacao(conteudo)

                        # Adicionar delimitadores e conteúdo ao arquivo de saída
                        f_saida.write("================================\n")
                        f_saida.write(f"TÍTULO: {arquivo}\n")
                        f_saida.write("================================\n")
                        f_saida.write(conteudo_limpo)
                        f_saida.write("\n\n")
                except UnicodeDecodeError:
                    f_saida.write("================================\n")
                    f_saida.write(f"TÍTULO: {arquivo}\n")
                    f_saida.write("================================\n")
                    f_saida.write("[Conteúdo não legível como texto]\n\n")

        # Retornar o arquivo como resposta para download
        with open(caminho_arquivo_saida, 'r', encoding='utf-8') as f:
            response = HttpResponse(f.read(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{nome_arquivo_saida}"'
            return response

    except Exception as e:
        # Retornar erro caso ocorra
        return HttpResponse(f"Erro ao processar arquivos: {str(e)}")
    # Renderizar a página de upload se não for POST
    return render(request, 'fileprocessor/upload.html')

# Página inicial simples
def home(request):
    return render(request, 'fileprocessor/home.html')

# Página index (caso necessário)
def index(request):
    return render(request, 'fileprocessor/index.html')

def salvar_estrutura_em_arquivo(estrutura):
    # Usando o MEDIA_ROOT corretamente configurado no settings.py
    arquivo_estrutura_path = os.path.join(settings.MEDIA_ROOT, 'estrutura.txt')

    # Salvar a estrutura no arquivo
    with open(arquivo_estrutura_path, 'w') as f:
        f.write(estrutura)

    print(f"Arquivo 'estrutura.txt' salvo em: {arquivo_estrutura_path}")

def arquivos_extraidos(request):
    # Caminho para a pasta onde os arquivos são armazenados
    media_path = os.path.join(settings.MEDIA_ROOT)
    
    # Obter todos os arquivos na pasta media
    arquivos = os.listdir(media_path)
    
    # Filtrar apenas arquivos (não diretórios)
    arquivos = [arquivo for arquivo in arquivos if os.path.isfile(os.path.join(media_path, arquivo))]
    
    # Passar os arquivos para o template
    return render(request, 'fileprocessor/extraidos.html', {'arquivos': arquivos})