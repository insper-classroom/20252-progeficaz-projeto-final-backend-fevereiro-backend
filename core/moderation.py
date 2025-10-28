import os
import requests
import json

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://openai-insper.openai.azure.com/openai/deployments/gpt-4_MarcioJunior_PECC/chat/completions"
AZURE_API_VERSION = "2025-01-01-preview"
AZURE_API_KEY = "a0d9b9f7c34d4662a90e2a829f572333"

def verificar_conteudo(texto):
    """
    Verifica se o conteúdo contém linguagem imprópria usando Azure OpenAI GPT-4.
    
    Returns:
        tuple: (is_safe: bool, flagged_categories: dict or None, error_message: str or None)
    """
    if not texto or not texto.strip():
        return True, None, None
    
    if not AZURE_API_KEY:
        print("⚠️  AZURE_OPENAI_API_KEY não configurada - moderação desabilitada")
        return True, None, None
    
    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_API_KEY
        }
        
        # Prompt para análise de moderação
        prompt = f"""Analise o seguinte texto e verifique se ele contém conteúdo inapropriado.

Texto: "{texto}"

Categorias a verificar:
- Conteúdo sexual explícito
- Violência ou ameaças
- Discriminação, racismo ou ódio
- Assédio
- Auto-mutilação ou suicídio
- Golpes ou fraudes
- Spam excessivo
- Palavrões ou linguagem ofensiva

Responda APENAS com um JSON no formato:
{{"is_safe": true/false, "category": "categoria detectada ou null", "reason": "explicação breve ou null"}}

Se o texto for seguro, retorne: {{"is_safe": true, "category": null, "reason": null}}
Se o texto for inapropriado, retorne: {{"is_safe": false, "category": "nome_da_categoria", "reason": "breve explicação"}}"""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um moderador de conteúdo rigoroso. Analise textos e identifique conteúdo inapropriado, incluindo palavrões, xingamentos e linguagem ofensiva. Responda sempre em JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.0,
            "max_tokens": 200
        }
        
        response = requests.post(
            f"{AZURE_OPENAI_ENDPOINT}?api-version={AZURE_API_VERSION}",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Erro na API Azure OpenAI: {response.status_code} - {response.text}")
            return True, None, None  # Em caso de erro, permitir o conteúdo
        
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        # Tentar extrair o JSON da resposta
        # Remover markdown se houver
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
            
        moderation_result = json.loads(content)
        
        if not moderation_result.get('is_safe', True):
            category = moderation_result.get('category', 'conteúdo inapropriado')
            reason = moderation_result.get('reason', 'detectado conteúdo inadequado')
            mensagem = f"Conteúdo bloqueado: {category} - {reason}"
            return False, {'category': category}, mensagem
        
        return True, None, None
            
    except json.JSONDecodeError as e:
        print(f"Erro ao parsear JSON da resposta de moderação: {e}")
        print(f"Resposta recebida: {content}")
        return True, None, None
    except requests.exceptions.Timeout:
        print("Timeout na verificação de moderação")
        return True, None, None
    except Exception as e:
        print(f"Erro ao verificar moderação: {e}")
        import traceback
        traceback.print_exc()
        return True, None, None


def verificar_thread(title, description=None):
    """
    Verifica título e descrição de uma thread.
    
    Returns:
        tuple: (is_safe: bool, error_message: str or None)
    """
    # Verificar título
    is_safe, _, mensagem = verificar_conteudo(title)
    if not is_safe:
        return False, f"Título impróprio: {mensagem}"
    
    # Verificar descrição se fornecida
    if description:
        is_safe, _, mensagem = verificar_conteudo(description)
        if not is_safe:
            return False, f"Descrição imprópria: {mensagem}"
    
    return True, None


def verificar_post(content):
    """
    Verifica o conteúdo de um post.
    
    Returns:
        tuple: (is_safe: bool, error_message: str or None)
    """
    is_safe, _, mensagem = verificar_conteudo(content)
    if not is_safe:
        return False, f"Conteúdo impróprio: {mensagem}"
    
    return True, None
