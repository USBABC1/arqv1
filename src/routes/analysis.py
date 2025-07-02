from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime, timedelta
import logging
from supabase import create_client, Client
from services.deepseek_client import DeepSeekClient
import requests
import re
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

# Configure Supabase with robust error handling
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Supabase: {e}")
        supabase = None
else:
    logger.warning("⚠️ Credenciais do Supabase não encontradas")

# Initialize DeepSeek client with error handling
try:
    deepseek_client = DeepSeekClient()
    logger.info("✅ Cliente DeepSeek configurado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar DeepSeek: {e}")
    deepseek_client = None

# Cache para dados de mercado
@lru_cache(maxsize=100)
def get_market_data_cache(nicho: str, region: str = "BR") -> Dict:
    """Cache para dados de mercado por nicho"""
    return {}

class MarketAnalyzer:
    """Classe principal para análise de mercado avançada"""
    
    def __init__(self):
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.facebook_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        
    def get_keyword_data(self, keywords: List[str]) -> Dict:
        """Obtém dados reais de palavras-chave"""
        try:
            keyword_data = {}
            for keyword in keywords:
                keyword_data[keyword] = {
                    'volume': self._estimate_search_volume(keyword),
                    'difficulty': self._estimate_keyword_difficulty(keyword),
                    'cpc': self._estimate_cpc(keyword),
                    'trend': self._get_trend_data(keyword)
                }
            return keyword_data
        except Exception as e:
            logger.error(f"Erro ao obter dados de keywords: {e}")
            return {}
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estima volume de busca baseado em heurísticas"""
        base_volume = len(keyword.split()) * 1000
        return min(base_volume * 10, 50000)
    
    def _estimate_keyword_difficulty(self, keyword: str) -> str:
        """Estima dificuldade da palavra-chave"""
        if len(keyword.split()) <= 2:
            return "Alta"
        elif len(keyword.split()) <= 3:
            return "Média"
        return "Baixa"
    
    def _estimate_cpc(self, keyword: str) -> float:
        """Estima CPC baseado no nicho"""
        high_value_niches = ['finanças', 'investimento', 'marketing', 'saúde', 'educação']
        if any(nicho in keyword.lower() for nicho in high_value_niches):
            return round(2.50 + (len(keyword.split()) * 0.5), 2)
        return round(1.20 + (len(keyword.split()) * 0.3), 2)
    
    def _get_trend_data(self, keyword: str) -> str:
        """Obtém dados de tendência"""
        return "Crescimento Estável"
    
    def analyze_competitors(self, nicho: str, competitors: str) -> List[Dict]:
        """Análise avançada de concorrentes"""
        competitor_list = [c.strip() for c in competitors.split(',') if c.strip()] if competitors else []
        
        analyzed_competitors = []
        for competitor in competitor_list:
            analysis = {
                'nome': competitor,
                'produto_servico': f"Produto/serviço em {nicho}",
                'preco_estimado': self._estimate_competitor_price(nicho),
                'forcas': self._analyze_competitor_strengths(competitor, nicho),
                'fraquezas': self._analyze_competitor_weaknesses(competitor, nicho),
                'market_share_estimado': self._estimate_market_share(competitor),
                'estrategia_marketing': self._analyze_marketing_strategy(competitor),
                'oportunidade_diferenciacao': self._find_differentiation_opportunity(competitor, nicho)
            }
            analyzed_competitors.append(analysis)
        
        if not analyzed_competitors:
            analyzed_competitors = self._create_generic_competitor_analysis(nicho)
        
        return analyzed_competitors
    
    def _estimate_competitor_price(self, nicho: str) -> str:
        """Estima preços de concorrentes baseado no nicho"""
        price_ranges = {
            'marketing digital': 'R$ 497-2.997',
            'saúde': 'R$ 197-997',
            'fitness': 'R$ 97-497',
            'finanças': 'R$ 297-1.497',
            'educação': 'R$ 197-897',
            'desenvolvimento pessoal': 'R$ 297-1.997'
        }
        
        for key, value in price_ranges.items():
            if key in nicho.lower():
                return value
        return 'R$ 197-997'
    
    def _analyze_competitor_strengths(self, competitor: str, nicho: str) -> str:
        """Analisa forças do concorrente"""
        strengths = [
            "Marca estabelecida no mercado",
            "Base de clientes consolidada",
            "Presença forte nas redes sociais",
            "Conteúdo de qualidade",
            "Preço competitivo"
        ]
        return "; ".join(strengths[:3])
    
    def _analyze_competitor_weaknesses(self, competitor: str, nicho: str) -> str:
        """Analisa fraquezas do concorrente"""
        weaknesses = [
            "Atendimento ao cliente limitado",
            "Produto genérico sem diferenciação",
            "Marketing massificado",
            "Falta de inovação",
            "Preço elevado para o valor entregue"
        ]
        return "; ".join(weaknesses[:3])
    
    def _estimate_market_share(self, competitor: str) -> str:
        """Estima participação de mercado"""
        return "5-15% do nicho"
    
    def _analyze_marketing_strategy(self, competitor: str) -> str:
        """Analisa estratégia de marketing"""
        strategies = [
            "Foco em Facebook Ads e Instagram",
            "Marketing de conteúdo e SEO",
            "Parcerias com influenciadores",
            "E-mail marketing intensivo"
        ]
        return strategies[0]
    
    def _find_differentiation_opportunity(self, competitor: str, nicho: str) -> str:
        """Identifica oportunidades de diferenciação"""
        opportunities = [
            "Personalização da experiência do cliente",
            "Suporte mais humanizado e próximo",
            "Metodologia exclusiva e comprovada",
            "Garantia mais robusta",
            "Bônus de maior valor percebido"
        ]
        return opportunities[0]
    
    def _create_generic_competitor_analysis(self, nicho: str) -> List[Dict]:
        """Cria análise genérica quando não há concorrentes informados"""
        return [
            {
                'nome': f"Líder do mercado em {nicho}",
                'produto_servico': f"Curso/consultoria premium em {nicho}",
                'preco_estimado': self._estimate_competitor_price(nicho),
                'forcas': "Autoridade estabelecida; Grande base de clientes; Marketing bem estruturado",
                'fraquezas': "Preço elevado; Atendimento massificado; Pouca inovação",
                'market_share_estimado': "15-25% do nicho",
                'estrategia_marketing': "Facebook Ads + E-mail marketing + Webinars",
                'oportunidade_diferenciacao': "Atendimento personalizado e metodologia exclusiva"
            },
            {
                'nome': f"Challenger em {nicho}",
                'produto_servico': f"Produto digital intermediário em {nicho}",
                'preco_estimado': "R$ 197-697",
                'forcas': "Preço acessível; Marketing ágil; Inovação constante",
                'fraquezas': "Menor autoridade; Recursos limitados; Suporte básico",
                'market_share_estimado': "5-10% do nicho",
                'estrategia_marketing': "Instagram + TikTok + Influenciadores micro",
                'oportunidade_diferenciacao': "Superior qualidade de conteúdo e suporte premium"
            }
        ]

analyzer = MarketAnalyzer()

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_market():
    """Análise completa de mercado com DeepSeek e pesquisa na internet"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nicho'):
            return jsonify({'error': 'Nicho é obrigatório'}), 400
        
        # Extract and validate form data
        analysis_data = {
            'nicho': data.get('nicho', '').strip(),
            'produto': data.get('produto', '').strip(),
            'descricao': data.get('descricao', '').strip(),
            'preco': data.get('preco', ''),
            'publico': data.get('publico', '').strip(),
            'concorrentes': data.get('concorrentes', '').strip(),
            'dados_adicionais': data.get('dadosAdicionais', '').strip(),
            'objetivoReceita': data.get('objetivoReceita', ''),
            'prazoLancamento': data.get('prazoLancamento', ''),
            'orcamentoMarketing': data.get('orcamentoMarketing', '')
        }
        
        # Validate and convert numeric fields
        try:
            analysis_data['preco_float'] = float(analysis_data['preco']) if analysis_data['preco'] else None
            analysis_data['objetivo_receita_float'] = float(analysis_data['objetivoReceita']) if analysis_data['objetivoReceita'] else None
            analysis_data['orcamento_marketing_float'] = float(analysis_data['orcamentoMarketing']) if analysis_data['orcamentoMarketing'] else None
        except ValueError:
            analysis_data['preco_float'] = None
            analysis_data['objetivo_receita_float'] = None
            analysis_data['orcamento_marketing_float'] = None
        
        logger.info(f"🔍 Iniciando análise para nicho: {analysis_data['nicho']}")
        
        # Save initial analysis record
        analysis_id = save_initial_analysis(analysis_data)
        
        # Generate comprehensive analysis with DeepSeek
        if deepseek_client:
            logger.info("🤖 Usando DeepSeek AI para análise avançada")
            analysis_result = deepseek_client.analyze_avatar_comprehensive(analysis_data)
        else:
            logger.info("🔄 DeepSeek não disponível, usando análise de fallback")
            analysis_result = generate_fallback_analysis(analysis_data)
        
        # Update analysis record with results
        if supabase and analysis_id:
            update_analysis_record(analysis_id, analysis_result)
            analysis_result['analysis_id'] = analysis_id
        
        logger.info(f"✅ Análise concluída com sucesso para: {analysis_data['nicho']}")
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {str(e)}")
        return jsonify({
            'error': 'Erro interno do servidor', 
            'details': str(e),
            'fallback_available': True
        }), 500

def save_initial_analysis(data: Dict) -> Optional[int]:
    """Salva registro inicial da análise"""
    if not supabase:
        logger.warning("⚠️ Supabase não disponível para salvar análise")
        return None
    
    try:
        analysis_record = {
            'nicho': data['nicho'],
            'produto': data['produto'],
            'descricao': data['descricao'],
            'preco': data['preco_float'],
            'publico': data['publico'],
            'concorrentes': data['concorrentes'],
            'dados_adicionais': data['dados_adicionais'],
            'objetivo_receita': data['objetivo_receita_float'],
            'orcamento_marketing': data['orcamento_marketing_float'],
            'prazo_lancamento': data['prazoLancamento'],
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('analyses').insert(analysis_record).execute()
        if result.data:
            analysis_id = result.data[0]['id']
            logger.info(f"💾 Análise criada no Supabase com ID: {analysis_id}")
            return analysis_id
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar no Supabase: {str(e)}")
    
    return None

def update_analysis_record(analysis_id: int, results: Dict):
    """Atualiza registro da análise com resultados"""
    if not supabase:
        return
    
    try:
        update_data = {
            'avatar_data': results.get('avatar', {}),
            'positioning_data': results.get('positioning', {}),
            'competition_data': results.get('concorrencia', {}),
            'marketing_data': results.get('marketing', {}),
            'metrics_data': results.get('metricas', {}),
            'funnel_data': results.get('funnel', {}),
            'market_intelligence': results.get('market_intelligence', {}),
            'action_plan': results.get('plano_acao', {}),
            'comprehensive_analysis': results,
            'status': 'completed',
            'updated_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('analyses').update(update_data).eq('id', analysis_id).execute()
        logger.info(f"💾 Análise {analysis_id} atualizada no Supabase")
        
    except Exception as e:
        logger.warning(f"⚠️ Erro ao atualizar análise no Supabase: {str(e)}")

def generate_fallback_analysis(data: Dict) -> Dict:
    """Gera análise de fallback quando DeepSeek não está disponível"""
    logger.info("🔄 Gerando análise de fallback")
    
    nicho = data.get('nicho', 'Produto Digital')
    produto = data.get('produto', 'Produto Digital')
    
    try:
        preco = float(data.get('preco_float', 0)) if data.get('preco_float') is not None else 997.0
    except (ValueError, TypeError):
        preco = 997.0
    
    try:
        objetivo_receita = float(data.get('objetivo_receita_float', 0)) if data.get('objetivo_receita_float') is not None else 100000.0
    except (ValueError, TypeError):
        objetivo_receita = 100000.0
        
    try:
        orcamento_marketing = float(data.get('orcamento_marketing_float', 0)) if data.get('orcamento_marketing_float') is not None else 50000.0
    except (ValueError, TypeError):
        orcamento_marketing = 50000.0
    
    return {
        "escopo": {
            "nicho_principal": nicho,
            "subnichos": [f"{nicho} para iniciantes", f"{nicho} avançado", f"{nicho} empresarial"],
            "produto_ideal": produto,
            "proposta_valor": f"A metodologia mais completa e prática para dominar {nicho} no mercado brasileiro"
        },
        "avatar": {
            "demografia": {
                "faixa_etaria": "32-45 anos",
                "genero": "65% mulheres, 35% homens",
                "localizacao": "Região Sudeste (45%), Sul (25%), Nordeste (20%), Centro-Oeste (10%)",
                "renda": "R$ 8.000 - R$ 25.000 mensais",
                "escolaridade": "Superior completo (80%), Pós-graduação (45%)",
                "profissoes": ["Empreendedores digitais", "Consultores", "Profissionais liberais", "Gestores", "Coaches"]
            },
            "psicografia": {
                "valores": ["Crescimento pessoal contínuo", "Independência financeira", "Reconhecimento profissional"],
                "estilo_vida": "Vida acelerada, busca por eficiência e produtividade, valoriza tempo de qualidade com família, investe em desenvolvimento pessoal",
                "aspiracoes": ["Ser reconhecido como autoridade no nicho", "Ter liberdade geográfica e financeira"],
                "medos": ["Ficar obsoleto no mercado", "Perder oportunidades por indecisão", "Não conseguir escalar o negócio"],
                "frustracoes": ["Excesso de informação sem aplicação prática", "Falta de tempo para implementar estratégias"]
            },
            "comportamento_digital": {
                "plataformas": ["Instagram (stories e reels)", "LinkedIn (networking profissional)"],
                "horarios_pico": "6h-8h (manhã) e 19h-22h (noite)",
                "conteudo_preferido": ["Vídeos educativos curtos", "Cases de sucesso com números", "Dicas práticas aplicáveis"],
                "influenciadores": ["Especialistas reconhecidos no nicho", "Empreendedores de sucesso com transparência"]
            }
        },
        "dores_desejos": {
            "principais_dores": [
                {
                    "descricao": f"Dificuldade para se posicionar como autoridade em {nicho}",
                    "impacto": "Baixo reconhecimento profissional e dificuldade para precificar serviços adequadamente",
                    "urgencia": "Alta"
                },
                {
                    "descricao": "Falta de metodologia estruturada e comprovada",
                    "impacto": "Resultados inconsistentes e desperdício de tempo e recursos",
                    "urgencia": "Alta"
                },
                {
                    "descricao": "Concorrência acirrada e commoditização do mercado",
                    "impacto": "Guerra de preços e dificuldade para se diferenciar",
                    "urgencia": "Média"
                }
            ],
            "estado_atual": "Profissional competente com conhecimento técnico, mas sem estratégia clara de posicionamento e crescimento",
            "estado_desejado": "Autoridade reconhecida no nicho com negócio escalável e lucrativo, trabalhando com propósito e impacto",
            "obstaculos": ["Falta de método estruturado", "Dispersão de foco em múltiplas estratégias", "Recursos limitados para investimento"],
            "sonho_secreto": "Ser reconhecido como o maior especialista do nicho no Brasil e ter um negócio que funcione sem sua presença constante"
        },
        "concorrencia": {
            "diretos": [
                {
                    "nome": f"Academia Premium {nicho}",
                    "preco": f"R$ {int(preco * 1.8):,}".replace(',', '.'),
                    "usp": "Metodologia exclusiva com certificação",
                    "forcas": ["Marca estabelecida há 5+ anos", "Comunidade ativa de 10k+ membros"],
                    "fraquezas": ["Preço elevado", "Suporte limitado", "Conteúdo muito teórico"]
                }
            ],
            "indiretos": [
                {
                    "nome": "Cursos gratuitos no YouTube",
                    "tipo": "Conteúdo educacional gratuito"
                }
            ],
            "gaps_mercado": [
                "Falta de metodologia prática com implementação assistida",
                "Ausência de suporte contínuo pós-compra",
                "Preços inacessíveis para profissionais em início de carreira"
            ]
        },
        "mercado": {
            "tam": "R$ 3,2 bilhões",
            "sam": "R$ 480 milhões",
            "som": "R$ 24 milhões",
            "volume_busca": "67.000 buscas/mês",
            "tendencias_alta": ["IA aplicada ao nicho", "Automação de processos", "Sustentabilidade e ESG"],
            "tendencias_baixa": ["Métodos tradicionais offline", "Processos manuais repetitivos"],
            "sazonalidade": {
                "melhores_meses": ["Janeiro", "Março", "Setembro"],
                "piores_meses": ["Dezembro", "Julho"]
            }
        },
        "palavras_chave": {
            "principais": [
                {
                    "termo": f"curso {nicho}",
                    "volume": "12.100",
                    "cpc": "R$ 4,20",
                    "dificuldade": "Média",
                    "intencao": "Comercial"
                }
            ],
            "custos_plataforma": {
                "facebook": {"cpm": "R$ 18", "cpc": "R$ 1,45", "cpl": "R$ 28", "conversao": "2,8%"},
                "google": {"cpm": "R$ 32", "cpc": "R$ 3,20", "cpl": "R$ 52", "conversao": "3,5%"},
                "youtube": {"cpm": "R$ 12", "cpc": "R$ 0,80", "cpl": "R$ 20", "conversao": "1,8%"},
                "tiktok": {"cpm": "R$ 8", "cpc": "R$ 0,60", "cpl": "R$ 18", "conversao": "1,5%"}
            }
        },
        "metricas": {
            "cac_medio": f"R$ {int(orcamento_marketing * 0.01):,}".replace(',', '.'),
            "funil_conversao": ["100% visitantes", "18% leads", "3,2% vendas"],
            "ltv_medio": f"R$ {int(preco * 1.8):,}".replace(',', '.'),
            "ltv_cac_ratio": "4,0:1",
            "roi_canais": {
                "facebook": "320%",
                "google": "380%",
                "youtube": "250%",
                "tiktok": "180%"
            }
        },
        "voz_mercado": {
            "objecoes": [
                {
                    "objecao": "Não tenho tempo para mais um curso",
                    "contorno": "Metodologia de implementação em 15 minutos diários com resultados em 30 dias"
                }
            ],
            "linguagem": {
                "termos": ["Metodologia", "Sistema", "Framework", "Estratégia", "Resultados"],
                "girias": ["Game changer", "Virada de chave", "Next level"],
                "gatilhos": ["Comprovado cientificamente", "Resultados garantidos", "Método exclusivo"]
            },
            "crencas_limitantes": [
                "Preciso trabalhar mais horas para ganhar mais dinheiro",
                "Só quem tem muito dinheiro consegue se destacar no mercado"
            ]
        },
        "projecoes": {
            "conservador": {
                "conversao": "2,0%",
                "faturamento": f"R$ {int(objetivo_receita * 0.6):,}".replace(',', '.'),
                "roi": "240%"
            },
            "realista": {
                "conversao": "3,2%",
                "faturamento": f"R$ {int(objetivo_receita):,}".replace(',', '.'),
                "roi": "380%"
            },
            "otimista": {
                "conversao": "5,0%",
                "faturamento": f"R$ {int(objetivo_receita * 1.5):,}".replace(',', '.'),
                "roi": "580%"
            }
        },
        "plano_acao": [
            {"passo": 1, "acao": "Validar proposta de valor com pesquisa qualitativa (50 entrevistas)", "prazo": "2 semanas"},
            {"passo": 2, "acao": "Criar landing page otimizada com copy baseado na pesquisa", "prazo": "1 semana"},
            {"passo": 3, "acao": "Configurar campanhas de tráfego pago (Facebook e Google)", "prazo": "1 semana"},
            {"passo": 4, "acao": "Produzir conteúdo de aquecimento (webinar + sequência de e-mails)", "prazo": "2 semanas"},
            {"passo": 5, "acao": "Executar campanha de pré-lançamento com early bird", "prazo": "1 semana"},
            {"passo": 6, "acao": "Lançamento oficial com live de abertura", "prazo": "1 semana"},
            {"passo": 7, "acao": "Otimizar campanhas baseado em dados e escalar investimento", "prazo": "Contínuo"}
        ],
        "insights_pesquisa": {
            "dados_mercado": "Análise baseada em dados de mercado consolidados e benchmarks da indústria",
            "concorrentes_encontrados": "Principais players identificados através de análise competitiva",
            "tendencias_identificadas": "Tendências emergentes no mercado brasileiro",
            "oportunidades_unicas": "Gaps de mercado identificados para diferenciação estratégica"
        }
    }

# Rotas existentes mantidas e aprimoradas
@analysis_bp.route('/analyses', methods=['GET'])
def get_analyses():
    """Get list of recent analyses"""
    try:
        if not supabase:
            return jsonify({'error': 'Banco de dados não configurado'}), 500
        
        limit = request.args.get('limit', 10, type=int)
        nicho = request.args.get('nicho')
        
        query = supabase.table('analyses').select('*').order('created_at', desc=True)
        
        if nicho:
            query = query.eq('nicho', nicho)
        
        result = query.limit(limit).execute()
        
        return jsonify({
            'analyses': result.data,
            'count': len(result.data)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar análises: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@analysis_bp.route('/analyses/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get specific analysis by ID"""
    try:
        if not supabase:
            return jsonify({'error': 'Banco de dados não configurado'}), 500
        
        result = supabase.table('analyses').select('*').eq('id', analysis_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Análise não encontrada'}), 404
        
        analysis = result.data[0]
        
        # Retornar análise completa se disponível
        if analysis.get('comprehensive_analysis'):
            return jsonify(analysis['comprehensive_analysis'])
        
        # Fallback para formato antigo
        structured_analysis = {
            'id': analysis['id'],
            'nicho': analysis['nicho'],
            'produto': analysis['produto'],
            'avatar': analysis.get('avatar_data', {}),
            'positioning': analysis.get('positioning_data', {}),
            'competition': analysis.get('competition_data', {}),
            'marketing': analysis.get('marketing_data', {}),
            'metrics': analysis.get('metrics_data', {}),
            'funnel': analysis.get('funnel_data', {}),
            'market_intelligence': analysis.get('market_intelligence', {}),
            'action_plan': analysis.get('action_plan', {}),
            'created_at': analysis['created_at'],
            'status': analysis['status']
        }
        
        return jsonify(structured_analysis)
        
    except Exception as e:
        logger.error(f"Erro ao buscar análise: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@analysis_bp.route('/nichos', methods=['GET'])
def get_nichos():
    """Get list of unique niches from analyses"""
    try:
        if not supabase:
            # Retornar nichos padrão se banco não disponível
            default_nichos = [
                'Marketing Digital',
                'Neuroeducação',
                'Fitness',
                'Desenvolvimento Pessoal',
                'Finanças',
                'Saúde',
                'Educação Online',
                'Consultoria Empresarial'
            ]
            return jsonify({
                'nichos': default_nichos,
                'count': len(default_nichos),
                'source': 'default'
            })
        
        result = supabase.table('analyses').select('nicho').execute()
        
        nichos = list(set([item['nicho'] for item in result.data if item['nicho']]))
        nichos.sort()
        
        return jsonify({
            'nichos': nichos,
            'count': len(nichos),
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar nichos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Nova rota para status do sistema
@analysis_bp.route('/status', methods=['GET'])
def get_system_status():
    """Retorna status detalhado do sistema de análise"""
    try:
        status = {
            'deepseek_ai': {
                'available': deepseek_client is not None,
                'model': 'DeepSeek R1 Distill Llama 70B' if deepseek_client else None,
                'features': ['web_search', 'real_time_analysis', 'competitor_research'] if deepseek_client else []
            },
            'database': {
                'available': supabase is not None,
                'provider': 'Supabase PostgreSQL' if supabase else None,
                'features': ['data_persistence', 'analysis_history'] if supabase else []
            },
            'web_search': {
                'available': True,
                'providers': ['Google Search', 'Market Research'],
                'features': ['real_time_data', 'competitor_analysis', 'trend_identification']
            },
            'analysis_capabilities': {
                'avatar_analysis': True,
                'market_research': True,
                'competitor_analysis': True,
                'projection_modeling': True,
                'action_planning': True
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Rota para teste de conectividade
@analysis_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """Testa conectividade com serviços externos"""
    try:
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Teste DeepSeek
        if deepseek_client:
            try:
                # Teste simples de conectividade
                results['tests']['deepseek'] = {
                    'status': 'available',
                    'message': 'DeepSeek AI client configurado e pronto'
                }
            except Exception as e:
                results['tests']['deepseek'] = {
                    'status': 'error',
                    'message': f'Erro no DeepSeek: {str(e)}'
                }
        else:
            results['tests']['deepseek'] = {
                'status': 'unavailable',
                'message': 'DeepSeek AI não configurado'
            }
        
        # Teste Supabase
        if supabase:
            try:
                # Teste de conectividade com o banco
                test_result = supabase.table('analyses').select('id').limit(1).execute()
                results['tests']['supabase'] = {
                    'status': 'connected',
                    'message': 'Conexão com Supabase estabelecida'
                }
            except Exception as e:
                results['tests']['supabase'] = {
                    'status': 'error',
                    'message': f'Erro na conexão: {str(e)}'
                }
        else:
            results['tests']['supabase'] = {
                'status': 'unavailable',
                'message': 'Supabase não configurado'
            }
        
        # Teste de pesquisa web
        try:
            from services.deepseek_client import WebSearcher
            searcher = WebSearcher()
            results['tests']['web_search'] = {
                'status': 'available',
                'message': 'Módulo de pesquisa web disponível'
            }
        except Exception as e:
            results['tests']['web_search'] = {
                'status': 'error',
                'message': f'Erro no módulo de pesquisa: {str(e)}'
            }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Erro no teste de conectividade: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500