"""
Filter Configuration for Forum Threads
This file contains all filter definitions and can be easily modified by developers.
"""

# ===== DEVELOPER CONFIGURATION SECTION =====
# Modify these dictionaries to change filter options

# Semester filter - Required, single selection
SEMESTERS = [
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
COURSES = [
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
SUBJECTS = {
    # Ciência da Computação
    "cc": {
        1: ["Matemática Discreta", "Introdução à Programação", "Lógica de Programação"],
        2: ["Estruturas de Dados", "Programação Orientada a Objetos", "Cálculo I"],
        3: ["Algoritmos e Complexidade", "Banco de Dados", "Programação Eficaz"],
        4: ["Sistemas Operacionais", "Redes de Computadores", "Engenharia de Software"],
        5: ["Inteligência Artificial", "Compiladores", "Análise de Sistemas"],
        6: ["Machine Learning", "Desenvolvimento Web", "Segurança da Informação"],
        7: ["Computação Gráfica", "Sistemas Distribuídos", "Projeto de Software"],
        8: ["Big Data", "Cloud Computing", "TCC I"],
        9: ["Internet das Coisas", "Blockchain", "TCC II"],
        10: ["Estágio Supervisionado", "Tópicos Especiais", "Empreendedorismo"]
    },
    # Administração
    "adm": {
        1: ["Matemática Aplicada", "Introdução à Administração", "Comunicação Empresarial"],
        2: ["Contabilidade Geral", "Economia", "Estatística"],
        3: ["Administração Financeira", "Marketing", "Gestão de Pessoas"],
        4: ["Administração de Produção", "Logística", "Direito Empresarial"],
        5: ["Planejamento Estratégico", "Administração de Projetos", "Comportamento Organizacional"],
        6: ["Gestão da Qualidade", "Comércio Exterior", "Empreendedorismo"],
        7: ["Consultoria Empresarial", "Gestão Ambiental", "Ética Empresarial"],
        8: ["TCC I", "Estágio Supervisionado I", "Negociação"],
        9: ["TCC II", "Estágio Supervisionado II", "Gestão de Mudanças"],
        10: ["Seminários de Administração", "Tópicos Especiais", "Gestão de Inovação"]
    },
    # Engenharia Civil
    "eng_civil": {
        1: ["Cálculo I", "Geometria Analítica", "Desenho Técnico"],
        2: ["Cálculo II", "Física I", "Álgebra Linear"],
        3: ["Cálculo III", "Física II", "Mecânica dos Sólidos"],
        4: ["Resistência dos Materiais", "Topografia", "Hidráulica"],
        5: ["Estruturas de Concreto", "Geotecnia", "Hidrologia"],
        6: ["Estruturas Metálicas", "Pavimentação", "Saneamento"],
        7: ["Pontes", "Construção Civil", "Instalações Prediais"],
        8: ["Gerenciamento de Obras", "Patologia das Construções", "TCC I"],
        9: ["Projeto Estrutural", "Sustentabilidade", "TCC II"],
        10: ["Estágio Supervisionado", "Perícia de Engenharia", "Empreendedorismo"]
    }
}

# Add subjects for courses that don't have specific mappings
DEFAULT_SUBJECTS = ["Matemática Geral", "Português", "História", "Filosofia", "Educação Física"]

# Filter configuration metadata
FILTER_CONFIG = {
    "semester": {
        "required": True,
        "multiple": False,
        "depends_on": [],
        "options": SEMESTERS
    },
    "course": {
        "required": False,
        "multiple": True,
        "depends_on": [],
        "options": COURSES
    },
    "subject": {
        "required": True,
        "multiple": True,
        "depends_on": ["course", "semester"],
        "searchable": True,
        "options": SUBJECTS  # Dynamic based on dependencies
    }
}

# ===== END DEVELOPER CONFIGURATION SECTION =====

def get_filter_config():
    """Return the complete filter configuration."""
    return FILTER_CONFIG

def get_semester_options():
    """Get all semester options."""
    return SEMESTERS

def get_course_options():
    """Get all course options."""
    return COURSES

def get_subject_options(course_ids=None, semester_id=None):
    """
    Get subject options based on selected courses and semester.
    Subject filter is always visible, but options change dynamically.
    
    Args:
        course_ids (list): List of selected course IDs
        semester_id (int): Selected semester ID
    
    Returns:
        list: Available subject options
    """
    subjects = set()
    
    # Ensure course_ids is a list even if empty
    if course_ids is None:
        course_ids = []
    
    # Case 1: No filters selected - show ALL subjects from all courses and semesters
    if not course_ids and not semester_id:
        for course_subjects in SUBJECTS.values():
            for semester_subjects in course_subjects.values():
                subjects.update(semester_subjects)
        subjects.update(DEFAULT_SUBJECTS)
        return sorted(list(subjects))
    
    # Case 2: Only semester selected - show all subjects for that semester across ALL courses
    if semester_id and not course_ids:
        for course_id in SUBJECTS.keys():
            if semester_id in SUBJECTS[course_id]:
                subjects.update(SUBJECTS[course_id][semester_id])
        # Always include default subjects when only semester is selected
        subjects.update(DEFAULT_SUBJECTS)
        return sorted(list(subjects))
    
    # Case 3: Only courses selected - show all subjects for those specific courses (all semesters)
    if course_ids and not semester_id:
        for course_id in course_ids:
            if course_id in SUBJECTS:
                for semester_subjects in SUBJECTS[course_id].values():
                    subjects.update(semester_subjects)
        # Only add default subjects if no specific course subjects found
        if not subjects:
            subjects.update(DEFAULT_SUBJECTS)
        return sorted(list(subjects))
    
    # Case 4: Both course and semester selected - show subjects for specific combinations
    if course_ids and semester_id:
        subjects_found = False
        for course_id in course_ids:
            if course_id in SUBJECTS and semester_id in SUBJECTS[course_id]:
                subjects.update(SUBJECTS[course_id][semester_id])
                subjects_found = True
        
        # If no specific subjects found for any of the course+semester combinations, 
        # include default subjects
        if not subjects_found:
            subjects.update(DEFAULT_SUBJECTS)
        
        return sorted(list(subjects))
    
    return sorted(list(subjects))

def search_subjects(query, course_ids=None, semester_id=None):
    """
    Search subjects by query string.
    
    Args:
        query (str): Search query
        course_ids (list): List of selected course IDs
        semester_id (int): Selected semester ID
    
    Returns:
        list: Filtered subject options matching the query
    """
    all_subjects = get_subject_options(course_ids, semester_id)
    query_lower = query.lower()
    
    return [subject for subject in all_subjects if query_lower in subject.lower()]
