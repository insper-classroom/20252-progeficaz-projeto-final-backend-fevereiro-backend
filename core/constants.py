# Filter Configuration for Forum Threads
# Semester filter - Required, single selection
SEMESTERS: list[dict] = [
    {"id": 1, "name": "1º Semestre"},
    {"id": 2, "name": "2º Semestre"},
    {"id": 3, "name": "3º Semestre"},
    {"id": 4, "name": "4º Semestre"},
    {"id": 5, "name": "5º Semestre"},
    {"id": 6, "name": "6º Semestre"},
    {"id": 7, "name": "7º Semestre"},
    {"id": 8, "name": "8º Semestre"},
    {"id": 9, "name": "9º Semestre"},
    {"id": 10, "name": "10º Semestre"},
]

# Course filter - Optional, multiple selection
COURSES: list[dict] = [
    {"id": "cc", "name": "Ciência da Computação"},
    {"id": "adm", "name": "Administração"},
    {"id": "eng_civil", "name": "Engenharia Civil"},
    {"id": "eng_mec", "name": "Engenharia Mecânica"},
    {"id": "eng_ele", "name": "Engenharia Elétrica"},
    {"id": "eng_comp", "name": "Engenharia de Computação"},
    {"id": "direito", "name": "Direito"},
    {"id": "medicina", "name": "Medicina"},
    {"id": "psicologia", "name": "Psicologia"},
]

# Subject filter - Required, multiple selection, depends on course and semester
SUBJECTS: dict[str, dict[int, list[str]]] = {
    # Ciência da Computação
    "cc": {
        1: ["Matemática Discreta", "Introdução à Programação", "Lógica de Programação"],
        2: ["Estruturas de Dados", "Programação Orientada a Objetos", "Cálculo I"],
        3: ["Algoritmos e Complexidade", "Banco de Dados", "Programação Eficaz"],
        4: ["Sistemas Operacionais", "Redes de Computadores", "Engenharia de Software"],
        5: ["Inteligência Artificial", "Compiladores", "Análise de Sistemas"],
    },
    # Administração
    "adm": {
        1: [
            "Matemática Aplicada",
            "Introdução à Administração",
            "Comunicação Empresarial",
        ],
        2: ["Contabilidade Geral", "Economia", "Estatística"],
        3: ["Administração Financeira", "Marketing", "Gestão de Pessoas"],
        4: ["Administração de Produção", "Logística", "Direito Empresarial"],
        5: [
            "Planejamento Estratégico",
            "Administração de Projetos",
            "Comportamento Organizacional",
        ],
    },
}

DEFAULT_SUBJECTS: list[str] = [
    "Matemática Geral",
    "Português",
    "História",
    "Filosofia",
    "Educação Física",
]

FILTER_CONFIG: dict[str, dict] = {
    "semester": {
        "required": True,
        "multiple": False,
        "depends_on": [],
        "options": SEMESTERS,
    },
    "course": {
        "required": False,
        "multiple": True,
        "depends_on": [],
        "options": COURSES,
    },
    "subject": {
        "required": True,
        "multiple": True,
        "depends_on": ["course", "semester"],
        "searchable": True,
        "options": SUBJECTS,
    },
}

# Report Types Configuration
REPORT_TYPES: list[dict] = [
    {"id": "sexual", "name": "Conteúdo Sexual", "description": "Conteúdo de natureza sexual explícita"},
    {"id": "violence", "name": "Violência", "description": "Conteúdo violento ou ameaçador"},
    {"id": "discrimination", "name": "Discriminação", "description": "Discurso de ódio ou discriminatório"},
    {"id": "scam", "name": "Enganoso/Golpe", "description": "Conteúdo fraudulento ou enganoso"},
    {"id": "self_harm", "name": "Auto-mutilação/Suicídio", "description": "Conteúdo relacionado a auto-mutilação ou suicídio"},
    {"id": "spam", "name": "Spam", "description": "Conteúdo repetitivo ou não solicitado"},
    {"id": "other", "name": "Outros", "description": "Outro tipo de problema (descreva)"},
]

# Allowed extensions for file uploads (e.g., avatars)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5 MB