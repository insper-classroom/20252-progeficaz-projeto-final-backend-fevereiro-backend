# from openai import OpenAI
# import os

# client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# def verificar_conteudo(texto):
#     """
#     Verifica se o conteúdo contém linguagem imprópria usando a API de moderação da OpenAI.
    
#     Returns:
#         tuple: (is_safe: bool, flagged_categories: dict or None, error_message: str or None)
#     """
#     if not texto or not texto.strip():
#         return True, None, None
    
#     try:
#         resposta = client.moderations.create(
#             model="omni-moderation-latest",
#             input=texto
#         )
#         resultado = resposta.results[0]
        
#         if resultado.flagged:
#             # Traduzir categorias para português
#             categorias_pt = {
#                 'sexual': 'conteúdo sexual',
#                 'hate': 'discurso de ódio',
#                 'harassment': 'assédio',
#                 'self-harm': 'automutilação',
#                 'sexual/minors': 'conteúdo sexual envolvendo menores',
#                 'hate/threatening': 'ameaças de ódio',
#                 'violence/graphic': 'violência gráfica',
#                 'self-harm/intent': 'intenção de automutilação',
#                 'self-harm/instructions': 'instruções de automutilação',
#                 'harassment/threatening': 'assédio com ameaças',
#                 'violence': 'violência'
#             }
            
#             # Obter categorias detectadas
#             categorias_detectadas = []
#             for categoria, flagged in resultado.categories.model_dump().items():
#                 if flagged:
#                     categorias_detectadas.append(categorias_pt.get(categoria, categoria))
            
#             mensagem = f"Conteúdo bloqueado por conter: {', '.join(categorias_detectadas)}"
#             return False, resultado.categories, mensagem
#         else:
#             return True, None, None
            
#     except Exception as e:
#         # Em caso de erro na API, permitir o conteúdo mas logar o erro
#         print(f"Erro ao verificar moderação: {e}")
#         return True, None, None


# def verificar_thread(title, description=None):
#     """
#     Verifica título e descrição de uma thread.
    
#     Returns:
#         tuple: (is_safe: bool, error_message: str or None)
#     """
#     # Verificar título
#     is_safe, _, mensagem = verificar_conteudo(title)
#     if not is_safe:
#         return False, f"Título impróprio: {mensagem}"
    
#     # Verificar descrição se fornecida
#     if description:
#         is_safe, _, mensagem = verificar_conteudo(description)
#         if not is_safe:
#             return False, f"Descrição imprópria: {mensagem}"
    
#     return True, None


# def verificar_post(content):
#     """
#     Verifica o conteúdo de um post.
    
#     Returns:
#         tuple: (is_safe: bool, error_message: str or None)
#     """
#     is_safe, _, mensagem = verificar_conteudo(content)
#     if not is_safe:
#         return False, f"Conteúdo impróprio: {mensagem}"
    
#     return True, None
