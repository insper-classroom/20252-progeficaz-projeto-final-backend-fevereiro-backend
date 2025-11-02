# API Documentation - Forum Backend

## Visão Geral

Esta é a documentação completa da API REST do sistema de fórum desenvolvido em Flask. A API suporta autenticação de usuários, criação de threads (perguntas), posts (respostas), sistema de votação, busca de conteúdo, moderação automática de conteúdo e sistema de denúncias.

**Stack Tecnológica:**
- Framework: Flask 2.3.3
- Database: MongoDB (MongoEngine ORM)
- Autenticação: JWT (Flask-JWT-Extended)
- Moderação: Azure OpenAI GPT-4
- Email: SMTP com templates Jinja2
- Python: 3.13

**Características Principais:**
- ✅ Autenticação baseada em email do Insper
- ✅ Verificação de email obrigatória
- ✅ Sistema de votação (upvote/downvote) com toggle
- ✅ Fixação de posts pelo dono da thread
- ✅ Moderação automática de conteúdo via IA
- ✅ Sistema de denúncias com múltiplas categorias
- ✅ Busca e filtros avançados
- ✅ Timezone automático (Brasília/UTC)

---

## Base URLs

- **Development:** `http://localhost:5000`
- **API Prefix:** `/api`

---

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Após o login, você receberá um token que deve ser incluído no header de todas as requisições protegidas:

```
Authorization: Bearer <seu_token_jwt>
```

**Duração do Token:** 1 hora (3600 segundos)

---

## TypeScript Types

```typescript
// ==================== User Types ====================
interface User {
  id: string;
  username: string;
  email: string;
}

interface RegisterRequest {
  email: string;      // Must be @insper.edu.br or @al.insper.edu.br
  password: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  message: string;
  access_token: string;
}

interface VerifyEmailRequest {
  authToken: string;  // Token received via email
}

interface ResendVerificationRequest {
  email: string;
}

// ==================== Thread Types ====================
interface Thread {
  id: string;
  author: string;
  title: string;               // max 200 chars
  description?: string;        // max 500 chars
  semester: number;            // 1-10
  courses: string[];           // Array of course IDs
  subjects: string[];          // Array of subject names
  score: number;               // upvotes - downvotes
  created_at: string;          // ISO 8601
  user_vote: 'upvote' | 'downvote' | null;
}

interface ThreadWithPosts extends Thread {
  posts: Post[];
}

interface CreateThreadRequest {
  title: string;               // Required, max 200 chars
  description?: string;        // Optional, max 500 chars
  semester: number;            // Required, 1-10
  courses?: string[];          // Optional, course IDs
  subjects?: string[];         // Optional, subject names
}

interface UpdateThreadRequest {
  title?: string;              // max 200 chars
  description?: string;        // max 500 chars
  semester?: number;           // 1-10
  courses?: string[];
  subjects?: string[];
}

interface ThreadsListResponse {
  threads: Thread[];
}

// ==================== Post Types ====================
interface Post {
  id: string;
  thread_id: string;
  author: string;
  content: string;
  pinned: boolean;
  score: number;               // upvotes - downvotes
  created_at: string;          // ISO 8601
  updated_at: string;          // ISO 8601
  user_vote: 'upvote' | 'downvote' | null;
}

interface CreatePostRequest {
  content: string;             // Required
}

interface UpdatePostRequest {
  content: string;             // Required
}

// ==================== Vote Types ====================
interface VoteResponse {
  message: string;
  score: number;
}

interface PinResponse {
  message: string;
  pinned: boolean;
}

// ==================== Search Types ====================
interface SearchThreadsResponse {
  query: string;
  count: number;
  results: SearchThreadResult[];
}

interface SearchThreadResult {
  id: string;
  title: string;
  description?: string;
  author: string;
  semester: number;
  courses: string[];
  subjects: string[];
  score: number;
  created_at: string;
  post_count: number;
}

// ==================== Filter Types ====================
interface FilterOption {
  id: string | number;
  name: string;
}

interface FilterConfig {
  semester: {
    required: boolean;
    multiple: boolean;
    depends_on: string[];
    options: FilterOption[];
  };
  course: {
    required: boolean;
    multiple: boolean;
    depends_on: string[];
    options: FilterOption[];
  };
  subject: {
    required: boolean;
    multiple: boolean;
    depends_on: string[];
    searchable: boolean;
    options: Record<string, Record<number, string[]>>;
  };
}

// ==================== Report Types ====================
type ReportType =
  | 'sexual'          // Conteúdo sexual explícito
  | 'violence'        // Violência ou ameaças
  | 'discrimination'  // Discriminação/discurso de ódio
  | 'scam'           // Golpe/fraude
  | 'self_harm'      // Auto-mutilação/suicídio
  | 'spam'           // Spam
  | 'other';         // Outros (requer descrição)

type ReportStatus =
  | 'pending'     // Aguardando análise
  | 'reviewed'    // Em análise
  | 'resolved'    // Resolvido
  | 'dismissed';  // Descartado

interface Report {
  id: string;
  reporter: string;
  content_type: 'thread' | 'post';
  content_id: string;
  report_type: ReportType;
  description?: string;
  status: ReportStatus;
  created_at: string;           // ISO 8601
}

interface CreateReportRequest {
  content_type: 'thread' | 'post';
  content_id: string;
  report_type: ReportType;
  description?: string;         // Required if report_type === 'other'
}

interface ReportTypeOption {
  id: ReportType;
  name: string;
  description: string;
}

interface ReportsListResponse {
  reports: Report[];
}

// ==================== Health Check Types ====================
interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  database: 'connected' | 'disconnected';
  error?: string;
}

interface DetailedHealthCheckResponse {
  timestamp: string;
  connection: {
    status: string;
    type: string;
    server_version: string;
    performance: {
      response_time_ms: number;
    };
  };
  database_operations: {
    status: string;
    operations: {
      insert: string;
      read: string;
      update: string;
      delete: string;
    };
  };
}

// ==================== Error Response ====================
interface ErrorResponse {
  error: string;
  details?: any;
}

interface SuccessResponse<T = any> {
  message?: string;
  [key: string]: T;
}
```

---

## Endpoints

### 1. Autenticação

#### 1.1. Registrar Usuário

Cria um novo usuário e envia email de verificação. O email deve ser do domínio Insper.

**Endpoint:** `POST /api/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```typescript
{
  email: string;      // Must be @insper.edu.br or @al.insper.edu.br
  password: string;
}
```

**Exemplo:**
```json
{
  "email": "joao.silva@al.insper.edu.br",
  "password": "senhaSegura123!"
}
```

**Response (201):**
```json
{
  "message": "Usuario registrado, email de verificação enviado!"
}
```

**Possíveis Erros:**
- `400` - Email ou senha faltando
- `400` - Usuário já existe
- `422` - Email em formato inválido
- `422` - Email não é do domínio Insper (@insper.edu.br ou @al.insper.edu.br)
- `500` - Falha ao enviar email de verificação

**Observações:**
- Username é extraído automaticamente do email (parte antes do @)
- Email de verificação enviado com token válido por 1 hora
- Conta permanece inativa até verificar o email
- Não é possível fazer login sem verificar o email

**Requer Autenticação:** ❌

---

#### 1.2. Verificar Email

Verifica o email do usuário usando o token recebido por email.

**Endpoint:** `POST /api/auth/verify-email`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```typescript
{
  authToken: string;  // Token recebido por email
}
```

**Exemplo:**
```json
{
  "authToken": "507f1f77bcf86cd799439011"
}
```

**Response (200):**
```json
{
  "message": "Email verificado com sucesso!"
}
```

**Possíveis Erros:**
- `400` - Token faltando
- `400` - Token inválido ou expirado
- `400` - Token já utilizado
- `404` - Usuário não encontrado

**Observações:**
- Token é válido por 1 hora após registro
- Após verificação, a conta é ativada e o usuário pode fazer login
- Token só pode ser usado uma vez

**Requer Autenticação:** ❌

---

#### 1.3. Reenviar Email de Verificação

Reenvia o email de verificação para usuários que ainda não verificaram sua conta.

**Endpoint:** `POST /api/auth/resend-verification`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```typescript
{
  email: string;
}
```

**Exemplo:**
```json
{
  "email": "joao.silva@al.insper.edu.br"
}
```

**Response (200):**
```json
{
  "message": "Email de verificação reenviado com sucesso!"
}
```

**Possíveis Erros:**
- `400` - Email faltando
- `400` - Email já verificado
- `404` - Usuário não encontrado
- `500` - Falha ao enviar email

**Observações:**
- Se já existe um token válido (não expirado), reutiliza o mesmo
- Se não existe ou expirou, cria um novo token
- Token tem validade de 1 hora

**Requer Autenticação:** ❌

---

#### 1.4. Login

Autentica o usuário e retorna um JWT token para uso nas requisições protegidas.

**Endpoint:** `POST /api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```typescript
{
  email: string;
  password: string;
}
```

**Exemplo:**
```json
{
  "email": "joao.silva@al.insper.edu.br",
  "password": "senhaSegura123!"
}
```

**Response (200):**
```json
{
  "message": "Login bem sucedido",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Possíveis Erros:**
- `400` - Email ou senha faltando
- `401` - Email ou senha inválidos
- `403` - Email não verificado (usuário deve verificar email primeiro)

**Observações:**
- Token JWT válido por 1 hora (3600 segundos)
- Usar token no header: `Authorization: Bearer <token>`
- Usuário deve ter verificado o email para fazer login

**Requer Autenticação:** ❌

---

#### 1.5. Obter Usuário Atual

Retorna informações do usuário autenticado.

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "username": "joao.silva",
  "email": "joao.silva@al.insper.edu.br"
}
```

**Possíveis Erros:**
- `401` - Token faltando ou inválido
- `404` - Usuário não encontrado

**Requer Autenticação:** ✅

---

### 2. Threads (Perguntas)

#### 2.1. Listar Threads

Lista todas as threads com filtros opcionais por semestre, curso e matéria.

**Endpoint:** `GET /api/threads`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```typescript
{
  semester?: number;      // Filter by semester (1-10)
  courses?: string[];     // Filter by course IDs (can repeat param)
  subjects?: string[];    // Filter by subject names (can repeat param)
}
```

**Exemplo:**
```
GET /api/threads
GET /api/threads?semester=3
GET /api/threads?semester=3&courses=cc&courses=adm
GET /api/threads?semester=3&courses=cc&subjects=Programação Eficaz&subjects=Banco de Dados
```

**Response (200):**
```json
{
  "threads": [
    {
      "id": "507f1f77bcf86cd799439011",
      "author": "joao.silva",
      "title": "Como implementar algoritmos de ordenação?",
      "description": "Estou com dúvida sobre quicksort e mergesort",
      "semester": 3,
      "courses": ["cc"],
      "subjects": ["Algoritmos e Complexidade"],
      "score": 5,
      "created_at": "2025-01-15T10:30:00-03:00",
      "user_vote": "upvote"
    },
    {
      "id": "507f1f77bcf86cd799439012",
      "author": "maria.santos",
      "title": "Dúvida sobre banco de dados relacionais",
      "description": null,
      "semester": 3,
      "courses": ["cc"],
      "subjects": ["Banco de Dados"],
      "score": 3,
      "created_at": "2025-01-15T09:00:00-03:00",
      "user_vote": null
    }
  ]
}
```

**Possíveis Erros:**
- `401` - Token inválido

**Observações:**
- Threads ordenadas por score (descendente) e depois por data de criação
- `user_vote` indica se o usuário atual votou na thread
- Filtros são opcionais e podem ser combinados
- Para múltiplos valores do mesmo filtro, repetir o parâmetro na query string

**Requer Autenticação:** ✅

---

#### 2.2. Criar Thread

Cria uma nova thread (pergunta). O conteúdo passa por moderação automática.

**Endpoint:** `POST /api/threads`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
{
  title: string;          // Required, max 200 chars
  description?: string;   // Optional, max 500 chars
  semester: number;       // Required, 1-10
  courses?: string[];     // Optional, course IDs
  subjects?: string[];    // Optional, subject names
}
```

**Exemplo:**
```json
{
  "title": "Como implementar autenticação JWT em Flask?",
  "description": "Estou desenvolvendo uma API e preciso implementar autenticação com JWT. Alguém pode me ajudar?",
  "semester": 3,
  "courses": ["cc"],
  "subjects": ["Programação Eficaz"]
}
```

**Response (201):**
```json
{
  "message": "Thread created successfully",
  "id": "507f1f77bcf86cd799439011",
  "author": "joao.silva",
  "title": "Como implementar autenticação JWT em Flask?",
  "description": "Estou desenvolvendo uma API e preciso implementar autenticação com JWT. Alguém pode me ajudar?",
  "semester": 3,
  "courses": ["cc"],
  "subjects": ["Programação Eficaz"],
  "score": 0,
  "created_at": "2025-01-15T10:30:00-03:00",
  "user_vote": null
}
```

**Possíveis Erros:**
- `400` - Título faltando
- `400` - Semestre inválido (deve ser 1-10)
- `400` - Título excede 200 caracteres
- `400` - Descrição excede 500 caracteres
- `400` - Falha na moderação de conteúdo (conteúdo inapropriado detectado)
- `500` - Erro no banco de dados

**Moderação de Conteúdo:**
O sistema verifica automaticamente o título e descrição para:
- Conteúdo sexual explícito
- Violência ou ameaças
- Discriminação/discurso de ódio
- Assédio
- Auto-mutilação/suicídio
- Golpes/fraudes
- Spam
- Linguagem ofensiva

Se conteúdo inapropriado for detectado, a thread não será criada e um erro será retornado.

**Requer Autenticação:** ✅

---

#### 2.3. Obter Thread com Posts

Retorna uma thread específica com todos os seus posts.

**Endpoint:** `GET /api/threads/<thread_id>`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
GET /api/threads/507f1f77bcf86cd799439011
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "author": "joao.silva",
  "title": "Como implementar autenticação JWT em Flask?",
  "description": "Estou desenvolvendo uma API...",
  "semester": 3,
  "courses": ["cc"],
  "subjects": ["Programação Eficaz"],
  "score": 5,
  "created_at": "2025-01-15T10:30:00-03:00",
  "user_vote": "upvote",
  "posts": [
    {
      "id": "507f1f77bcf86cd799439012",
      "thread_id": "507f1f77bcf86cd799439011",
      "author": "maria.santos",
      "content": "Você pode usar a biblioteca Flask-JWT-Extended. Aqui está um exemplo...",
      "pinned": true,
      "score": 8,
      "created_at": "2025-01-15T11:00:00-03:00",
      "updated_at": "2025-01-15T11:00:00-03:00",
      "user_vote": "upvote"
    },
    {
      "id": "507f1f77bcf86cd799439013",
      "thread_id": "507f1f77bcf86cd799439011",
      "author": "carlos.lima",
      "content": "Além da resposta acima, recomendo ler a documentação oficial...",
      "pinned": false,
      "score": 3,
      "created_at": "2025-01-15T12:00:00-03:00",
      "updated_at": "2025-01-15T12:00:00-03:00",
      "user_vote": null
    }
  ]
}
```

**Possíveis Erros:**
- `404` - Thread não encontrada
- `400` - ID de thread inválido

**Observações:**
- Posts ordenados por: fixados primeiro, depois por score, depois por data
- `user_vote` indica voto do usuário atual em cada post
- `pinned` indica se o post foi fixado pelo dono da thread

**Requer Autenticação:** ✅

---

#### 2.4. Atualizar Thread

Atualiza uma thread existente. Apenas o autor pode atualizar. O novo conteúdo passa por moderação.

**Endpoint:** `PUT /api/threads/<thread_id>`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
{
  title?: string;         // max 200 chars
  description?: string;   // max 500 chars
  semester?: number;      // 1-10
  courses?: string[];
  subjects?: string[];
}
```

**Exemplo:**
```json
{
  "title": "Como implementar autenticação JWT em Flask? [RESOLVIDO]",
  "description": "Estou desenvolvendo uma API... (Atualização: problema resolvido!)",
  "semester": 3
}
```

**Response (201):**
```json
{
  "message": "Thread updated successfully"
}
```

**Possíveis Erros:**
- `400` - Título ou descrição excede limite de caracteres
- `400` - Semestre inválido
- `400` - Falha na moderação de conteúdo
- `403` - Apenas o autor pode atualizar a thread
- `404` - Thread não encontrada

**Requer Autenticação:** ✅
**Autorização:** Apenas autor da thread

---

#### 2.5. Deletar Thread

Deleta uma thread e todos os seus posts associados. Apenas o autor pode deletar.

**Endpoint:** `DELETE /api/threads/<thread_id>`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
DELETE /api/threads/507f1f77bcf86cd799439011
```

**Response (200):**
```json
{
  "message": "Thread and associated posts deleted successfully"
}
```

**Possíveis Erros:**
- `403` - Apenas o autor pode deletar a thread
- `404` - Thread não encontrada

**Observações:**
- Todos os posts da thread são deletados em cascata
- Esta ação é irreversível

**Requer Autenticação:** ✅
**Autorização:** Apenas autor da thread

---

### 3. Posts (Respostas)

#### 3.1. Criar Post

Cria um novo post (resposta) em uma thread. O conteúdo passa por moderação automática.

**Endpoint:** `POST /api/threads/<thread_id>/posts`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
{
  content: string;  // Required
}
```

**Exemplo:**
```json
{
  "content": "Você pode usar a biblioteca Flask-JWT-Extended. Primeiro instale com pip install flask-jwt-extended, depois configure no seu app..."
}
```

**Response (201):**
```json
{
  "message": "Post created successfully",
  "id": "507f1f77bcf86cd799439012",
  "thread_id": "507f1f77bcf86cd799439011",
  "author": "maria.santos",
  "content": "Você pode usar a biblioteca Flask-JWT-Extended...",
  "pinned": false,
  "score": 0,
  "created_at": "2025-01-15T11:00:00-03:00",
  "updated_at": "2025-01-15T11:00:00-03:00",
  "user_vote": null
}
```

**Possíveis Erros:**
- `400` - Conteúdo faltando
- `400` - Falha na moderação de conteúdo (conteúdo inapropriado detectado)
- `404` - Thread não encontrada

**Moderação de Conteúdo:**
O conteúdo do post é verificado automaticamente para conteúdo inapropriado.

**Requer Autenticação:** ✅

---

#### 3.2. Obter Post

Retorna um post específico.

**Endpoint:** `GET /api/posts/<post_id>`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
GET /api/posts/507f1f77bcf86cd799439012
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "thread_id": "507f1f77bcf86cd799439011",
  "author": "maria.santos",
  "content": "Você pode usar a biblioteca Flask-JWT-Extended...",
  "pinned": false,
  "score": 8,
  "created_at": "2025-01-15T11:00:00-03:00",
  "updated_at": "2025-01-15T11:05:00-03:00",
  "user_vote": "upvote"
}
```

**Possíveis Erros:**
- `404` - Post não encontrado
- `400` - ID de post inválido

**Requer Autenticação:** ✅

---

#### 3.3. Atualizar Post

Atualiza o conteúdo de um post. Apenas o autor pode atualizar. O novo conteúdo passa por moderação.

**Endpoint:** `PUT /api/posts/<post_id>`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
{
  content: string;  // Required
}
```

**Exemplo:**
```json
{
  "content": "Você pode usar a biblioteca Flask-JWT-Extended. Primeiro instale com pip install flask-jwt-extended... [EDITADO: adicionei mais detalhes]"
}
```

**Response (201):**
```json
{
  "message": "Post updated successfully"
}
```

**Possíveis Erros:**
- `400` - Conteúdo faltando
- `400` - Falha na moderação de conteúdo
- `403` - Apenas o autor pode atualizar o post
- `404` - Post não encontrado

**Observações:**
- `updated_at` timestamp é atualizado automaticamente

**Requer Autenticação:** ✅
**Autorização:** Apenas autor do post

---

#### 3.4. Deletar Post

Deleta um post. Apenas o autor pode deletar.

**Endpoint:** `DELETE /api/posts/<post_id>`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
DELETE /api/posts/507f1f77bcf86cd799439012
```

**Response (200):**
```json
{
  "message": "Post deleted successfully"
}
```

**Possíveis Erros:**
- `403` - Apenas o autor pode deletar o post
- `404` - Post não encontrado

**Observações:**
- Esta ação é irreversível
- O post é removido da thread permanentemente

**Requer Autenticação:** ✅
**Autorização:** Apenas autor do post

---

### 4. Sistema de Votação

#### 4.1. Upvote (Thread ou Post)

Adiciona um upvote (voto positivo) em uma thread ou post. Sistema toggle: clicar novamente remove o voto.

**Endpoint:** `POST /api/<obj_type>/<object_id>/upvote`

**URL Parameters:**
- `obj_type`: `"threads"` ou `"posts"`
- `object_id`: ID da thread ou post

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
POST /api/threads/507f1f77bcf86cd799439011/upvote
POST /api/posts/507f1f77bcf86cd799439012/upvote
```

**Response (201):**
```json
{
  "message": "threads upvoted successfully",
  "score": 5
}
```

**Comportamento do Sistema de Votação:**
1. **Primeiro upvote:** Adiciona voto positivo (+1)
2. **Segundo upvote do mesmo usuário:** Remove o voto (toggle, score volta ao anterior)
3. **Se usuário já deu downvote:** Muda de downvote para upvote (+2 no score total)
4. **Usuários não podem votar em seu próprio conteúdo**

**Possíveis Erros:**
- `404` - Objeto não encontrado
- `400` - ID de objeto inválido
- `400` - obj_type inválido (deve ser "threads" ou "posts")

**Observações:**
- Score é calculado como: número de upvotes - número de downvotes
- Votos são anônimos (outros usuários não veem quem votou)
- Sistema previne auto-votação

**Requer Autenticação:** ✅

---

#### 4.2. Downvote (Thread ou Post)

Adiciona um downvote (voto negativo) em uma thread ou post. Sistema toggle: clicar novamente remove o voto.

**Endpoint:** `POST /api/<obj_type>/<object_id>/downvote`

**URL Parameters:**
- `obj_type`: `"threads"` ou `"posts"`
- `object_id`: ID da thread ou post

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
POST /api/threads/507f1f77bcf86cd799439011/downvote
POST /api/posts/507f1f77bcf86cd799439012/downvote
```

**Response (201):**
```json
{
  "message": "threads downvoted successfully",
  "score": -2
}
```

**Comportamento do Sistema de Votação:**
1. **Primeiro downvote:** Adiciona voto negativo (-1)
2. **Segundo downvote do mesmo usuário:** Remove o voto (toggle, score volta ao anterior)
3. **Se usuário já deu upvote:** Muda de upvote para downvote (-2 no score total)
4. **Usuários não podem votar em seu próprio conteúdo**

**Possíveis Erros:**
- `404` - Objeto não encontrado
- `400` - ID de objeto inválido
- `400` - obj_type inválido

**Requer Autenticação:** ✅

---

### 5. Pin/Unpin Posts

#### 5.1. Fixar Post

Fixa um post no topo da thread. Apenas o dono da thread pode fixar posts.

**Endpoint:** `POST /api/posts/<post_id>/pin`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
POST /api/posts/507f1f77bcf86cd799439012/pin
```

**Response (200):**
```json
{
  "message": "Post pinned successfully",
  "pinned": true
}
```

**Possíveis Erros:**
- `403` - Apenas o dono da thread pode fixar posts
- `404` - Post não encontrado

**Observações:**
- Posts fixados aparecem primeiro na lista de posts da thread
- Múltiplos posts podem ser fixados na mesma thread
- Posts fixados são ordenados por score entre si

**Requer Autenticação:** ✅
**Autorização:** Apenas dono da thread

---

#### 5.2. Desfixar Post

Remove a fixação de um post. Apenas o dono da thread pode desfixar posts.

**Endpoint:** `DELETE /api/posts/<post_id>/pin`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
DELETE /api/posts/507f1f77bcf86cd799439012/pin
```

**Response (200):**
```json
{
  "message": "Post unpinned successfully",
  "pinned": false
}
```

**Possíveis Erros:**
- `403` - Apenas o dono da thread pode desfixar posts
- `404` - Post não encontrado

**Requer Autenticação:** ✅
**Autorização:** Apenas dono da thread

---

### 6. Busca e Filtros

#### 6.1. Obter Configuração de Filtros

Retorna a configuração completa de todos os filtros disponíveis (semestres, cursos e matérias).

**Endpoint:** `GET /api/filters/config`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "semester": {
    "required": true,
    "multiple": false,
    "depends_on": [],
    "options": [
      {"id": 1, "name": "1º Semestre"},
      {"id": 2, "name": "2º Semestre"},
      {"id": 3, "name": "3º Semestre"},
      {"id": 4, "name": "4º Semestre"},
      {"id": 5, "name": "5º Semestre"},
      {"id": 6, "name": "6º Semestre"},
      {"id": 7, "name": "7º Semestre"},
      {"id": 8, "name": "8º Semestre"},
      {"id": 9, "name": "9º Semestre"},
      {"id": 10, "name": "10º Semestre"}
    ]
  },
  "course": {
    "required": false,
    "multiple": true,
    "depends_on": [],
    "options": [
      {"id": "cc", "name": "Ciência da Computação"},
      {"id": "adm", "name": "Administração"},
      {"id": "eng_civil", "name": "Engenharia Civil"},
      {"id": "eng_mec", "name": "Engenharia Mecânica"},
      {"id": "eng_ele", "name": "Engenharia Elétrica"},
      {"id": "eng_comp", "name": "Engenharia de Computação"},
      {"id": "direito", "name": "Direito"},
      {"id": "medicina", "name": "Medicina"},
      {"id": "psicologia", "name": "Psicologia"}
    ]
  },
  "subject": {
    "required": true,
    "multiple": true,
    "depends_on": ["course", "semester"],
    "searchable": true,
    "options": {
      "cc": {
        "1": ["Matemática Discreta", "Introdução à Programação", "Lógica de Programação"],
        "2": ["Estruturas de Dados", "Programação Orientada a Objetos", "Cálculo I"],
        "3": ["Algoritmos e Complexidade", "Banco de Dados", "Programação Eficaz"],
        "4": ["Sistemas Operacionais", "Redes de Computadores", "Engenharia de Software"],
        "5": ["Inteligência Artificial", "Compiladores", "Análise de Sistemas"]
      },
      "adm": {
        "1": ["Matemática Aplicada", "Introdução à Administração", "Comunicação Empresarial"],
        "2": ["Contabilidade Geral", "Economia", "Estatística"],
        "3": ["Administração Financeira", "Marketing", "Gestão de Pessoas"],
        "4": ["Administração de Produção", "Logística", "Direito Empresarial"],
        "5": ["Planejamento Estratégico", "Administração de Projetos", "Comportamento Organizacional"]
      }
    }
  }
}
```

**Observações:**
- `required`: Se o filtro é obrigatório para criar threads
- `multiple`: Se permite seleção múltipla
- `depends_on`: Filtros dos quais este filtro depende
- `searchable`: Se suporta busca textual (apenas subjects)
- Matérias incluem também `DEFAULT_SUBJECTS`: Matemática Geral, Português, História, Filosofia, Educação Física

**Requer Autenticação:** ✅

---

#### 6.2. Obter Opções de Filtro por Tipo

Retorna as opções de um filtro específico (semestres, cursos ou matérias).

**Endpoint:** `GET /api/filters/<filter_type>`

**URL Parameters:**
- `filter_type`: `"semesters"`, `"courses"`, ou `"subjects"`

**Query Parameters (apenas para subjects):**
```typescript
{
  courses?: string[];   // Course IDs to filter subjects
  semester?: number;    // Semester ID to filter subjects
  q?: string;          // Search query for subjects
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplos:**
```
GET /api/filters/semesters
GET /api/filters/courses
GET /api/filters/subjects
GET /api/filters/subjects?courses=cc&semester=3
GET /api/filters/subjects?courses=cc&courses=adm&semester=3
GET /api/filters/subjects?q=programação
```

**Response (200) para semesters:**
```json
[
  {"id": 1, "name": "1º Semestre"},
  {"id": 2, "name": "2º Semestre"},
  {"id": 3, "name": "3º Semestre"},
  {"id": 4, "name": "4º Semestre"},
  {"id": 5, "name": "5º Semestre"},
  {"id": 6, "name": "6º Semestre"},
  {"id": 7, "name": "7º Semestre"},
  {"id": 8, "name": "8º Semestre"},
  {"id": 9, "name": "9º Semestre"},
  {"id": 10, "name": "10º Semestre"}
]
```

**Response (200) para courses:**
```json
[
  {"id": "cc", "name": "Ciência da Computação"},
  {"id": "adm", "name": "Administração"},
  {"id": "eng_civil", "name": "Engenharia Civil"},
  {"id": "eng_mec", "name": "Engenharia Mecânica"},
  {"id": "eng_ele", "name": "Engenharia Elétrica"},
  {"id": "eng_comp", "name": "Engenharia de Computação"},
  {"id": "direito", "name": "Direito"},
  {"id": "medicina", "name": "Medicina"},
  {"id": "psicologia", "name": "Psicologia"}
]
```

**Response (200) para subjects (sem filtros):**
```json
[
  "Algoritmos e Complexidade",
  "Banco de Dados",
  "Programação Eficaz",
  "Administração Financeira",
  "Marketing",
  "Matemática Geral",
  "Português",
  "História",
  "Filosofia",
  "Educação Física"
]
```

**Response (200) para subjects (com filtros courses=cc&semester=3):**
```json
[
  "Algoritmos e Complexidade",
  "Banco de Dados",
  "Programação Eficaz"
]
```

**Response (200) para subjects (com busca q=programação):**
```json
[
  "Introdução à Programação",
  "Lógica de Programação",
  "Programação Orientada a Objetos",
  "Programação Eficaz"
]
```

**Observações:**
- Subjects sem filtros retorna todas as matérias de todos os cursos/semestres + DEFAULT_SUBJECTS
- Subjects com filtro de curso retorna matérias daquele(s) curso(s)
- Subjects com filtro de semestre retorna matérias daquele semestre
- Subjects com ambos filtros retorna matérias específicas do curso E semestre
- Busca (q) é case-insensitive e busca substring
- Lista é ordenada alfabeticamente e sem duplicatas

**Requer Autenticação:** ✅

---

#### 6.3. Buscar Threads

Busca threads por título com filtros opcionais.

**Endpoint:** `GET /api/search/threads`

**Query Parameters:**
```typescript
{
  q: string;            // Required: search query
  semester?: number;    // Filter by semester
  courses?: string[];   // Filter by courses
  subjects?: string[];  // Filter by subjects
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
GET /api/search/threads?q=JWT
GET /api/search/threads?q=JWT&semester=3
GET /api/search/threads?q=algoritmo&semester=3&courses=cc
GET /api/search/threads?q=banco&semester=3&courses=cc&subjects=Banco de Dados
```

**Response (200):**
```json
{
  "query": "JWT",
  "count": 2,
  "results": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Como implementar autenticação JWT em Flask?",
      "description": "Estou desenvolvendo uma API...",
      "author": "joao.silva",
      "semester": 3,
      "courses": ["cc"],
      "subjects": ["Programação Eficaz"],
      "score": 8,
      "created_at": "2025-01-15T10:30:00-03:00",
      "post_count": 5
    },
    {
      "id": "507f1f77bcf86cd799439015",
      "title": "JWT vs Session: qual usar?",
      "description": "Quais as vantagens e desvantagens?",
      "author": "maria.santos",
      "semester": 3,
      "courses": ["cc"],
      "subjects": ["Programação Eficaz"],
      "score": 3,
      "created_at": "2025-01-14T15:00:00-03:00",
      "post_count": 2
    }
  ]
}
```

**Possíveis Erros:**
- `400` - Query de busca faltando (parâmetro `q` é obrigatório)

**Observações:**
- Busca é case-insensitive
- Busca apenas no campo `title` das threads
- Resultados incluem contagem de posts (`post_count`)
- Filtros são opcionais e podem ser combinados
- Resultados ordenados por relevância

**Requer Autenticação:** ✅

---

### 7. Sistema de Denúncias/Reports

#### 7.1. Criar Denúncia

Cria uma denúncia de conteúdo inapropriado (thread ou post).

**Endpoint:** `POST /api/reports`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
{
  content_type: 'thread' | 'post';  // Required
  content_id: string;                // Required: ID of the content
  report_type: ReportType;           // Required
  description?: string;              // Required if report_type === 'other', max 500 chars
}

// Available Report Types:
type ReportType =
  | 'sexual'          // Conteúdo sexual explícito
  | 'violence'        // Conteúdo violento ou ameaçador
  | 'discrimination'  // Discriminação/discurso de ódio
  | 'scam'           // Golpe/fraude
  | 'self_harm'      // Auto-mutilação/suicídio
  | 'spam'           // Spam
  | 'other';         // Outro (requer descrição)
```

**Exemplo:**
```json
{
  "content_type": "post",
  "content_id": "507f1f77bcf86cd799439012",
  "report_type": "spam",
  "description": "Este usuário está fazendo propaganda não relacionada ao tópico"
}
```

**Response (201):**
```json
{
  "message": "Report created successfully",
  "id": "507f1f77bcf86cd799439020",
  "reporter": "joao.silva",
  "content_type": "post",
  "content_id": "507f1f77bcf86cd799439012",
  "report_type": "spam",
  "description": "Este usuário está fazendo propaganda não relacionada ao tópico",
  "status": "pending",
  "created_at": "2025-01-15T12:00:00-03:00"
}
```

**Possíveis Erros:**
- `400` - content_type inválido (deve ser "thread" ou "post")
- `400` - report_type inválido
- `400` - Campos obrigatórios faltando
- `400` - Descrição obrigatória quando report_type é "other"
- `400` - Descrição excede 500 caracteres
- `400` - Usuário já denunciou este conteúdo (não pode denunciar duas vezes)
- `404` - Conteúdo não encontrado

**Observações:**
- Cada usuário pode denunciar um conteúdo apenas uma vez
- Descrição é opcional para tipos pré-definidos, mas obrigatória para "other"
- Status inicial é sempre "pending"
- Denúncias são anônimas para o autor do conteúdo

**Report Types Disponíveis:**

| ID | Nome | Descrição |
|----|------|-----------|
| `sexual` | Conteúdo Sexual | Conteúdo de natureza sexual explícita |
| `violence` | Violência | Conteúdo violento ou ameaçador |
| `discrimination` | Discriminação | Discurso de ódio ou discriminatório |
| `scam` | Enganoso/Golpe | Conteúdo fraudulento ou enganoso |
| `self_harm` | Auto-mutilação/Suicídio | Conteúdo relacionado a auto-mutilação ou suicídio |
| `spam` | Spam | Conteúdo repetitivo ou não solicitado |
| `other` | Outros | Outro tipo de problema (requer descrição) |

**Requer Autenticação:** ✅

---

#### 7.2. Listar Denúncias

Lista todas as denúncias do sistema. (Futuramente será restrito a administradores)

**Endpoint:** `GET /api/reports`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "reports": [
    {
      "id": "507f1f77bcf86cd799439020",
      "reporter": "joao.silva",
      "content_type": "post",
      "content_id": "507f1f77bcf86cd799439012",
      "report_type": "spam",
      "description": "Este usuário está fazendo propaganda não relacionada ao tópico",
      "status": "pending",
      "created_at": "2025-01-15T12:00:00-03:00"
    },
    {
      "id": "507f1f77bcf86cd799439021",
      "reporter": "maria.santos",
      "content_type": "thread",
      "content_id": "507f1f77bcf86cd799439015",
      "report_type": "discrimination",
      "description": "Conteúdo discriminatório contra grupo específico",
      "status": "reviewed",
      "created_at": "2025-01-14T18:30:00-03:00"
    }
  ]
}
```

**Observações:**
- Ordenado por data de criação (mais recentes primeiro)
- Status pode ser: pending, reviewed, resolved, dismissed

**Status Possíveis:**
- `pending`: Aguardando análise
- `reviewed`: Em análise
- `resolved`: Resolvido (ação tomada)
- `dismissed`: Descartado (não procede)

**Requer Autenticação:** ✅

---

#### 7.3. Obter Denúncia por ID

Retorna uma denúncia específica.

**Endpoint:** `GET /api/reports/<report_id>`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Exemplo:**
```
GET /api/reports/507f1f77bcf86cd799439020
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439020",
  "reporter": "joao.silva",
  "content_type": "post",
  "content_id": "507f1f77bcf86cd799439012",
  "report_type": "spam",
  "description": "Este usuário está fazendo propaganda não relacionada ao tópico",
  "status": "pending",
  "created_at": "2025-01-15T12:00:00-03:00"
}
```

**Possíveis Erros:**
- `404` - Denúncia não encontrada
- `400` - ID de denúncia inválido

**Requer Autenticação:** ✅

---

### 8. Health Check

#### 8.1. Health Check Simples

Verifica se a API e o banco de dados estão funcionando.

**Endpoint:** `GET /health`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200) - Sistema Saudável:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (503) - Sistema com Problemas:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "Connection refused"
}
```

**Observações:**
- Usa código 200 quando tudo está OK
- Usa código 503 (Service Unavailable) quando há problemas
- Testa conexão com MongoDB fazendo uma query simples

**Requer Autenticação:** ✅

---

#### 8.2. Health Check Detalhado

Verifica detalhadamente o status da API, banco de dados e operações CRUD.

**Endpoint:** `GET /health/detailed`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "timestamp": "2025-01-15T10:30:00-03:00",
  "connection": {
    "status": "connected",
    "type": "mongodb",
    "server_version": "7.0.0",
    "performance": {
      "response_time_ms": 2.45
    }
  },
  "database_operations": {
    "status": "operational",
    "operations": {
      "insert": "success",
      "read": "success",
      "update": "success",
      "delete": "success"
    }
  }
}
```

**Response (503) - Banco Desconectado:**
```json
{
  "timestamp": "2025-01-15T10:30:00-03:00",
  "connection": {
    "status": "disconnected",
    "error": "Connection timeout"
  }
}
```

**Observações:**
- Testa todas as operações CRUD (Create, Read, Update, Delete)
- Mede tempo de resposta do banco
- Retorna versão do servidor MongoDB
- Timestamp no timezone de Brasília

**Requer Autenticação:** ✅

---

### 9. API Root

#### 9.1. Obter Índice da API

Retorna informações gerais sobre a API e suas rotas disponíveis.

**Endpoint:** `GET /`

**Response (200):**
```json
{
  "info": {
    "title": "Forum API",
    "version": "1.0.0",
    "description": "API for managing forum threads and search filters"
  },
  "routes": {
    "/api": "Authentication, threads, posts, filters, search, reports",
    "/health": "Health check endpoints"
  }
}
```

**Requer Autenticação:** ❌

---

## Códigos de Status HTTP

| Código | Significado | Quando Usar |
|--------|-------------|-------------|
| 200 | OK | Requisição bem-sucedida (GET, DELETE) |
| 201 | Created | Recurso criado/atualizado com sucesso (POST, PUT) |
| 400 | Bad Request | Erro de validação ou dados inválidos |
| 401 | Unauthorized | Token JWT faltando ou inválido |
| 403 | Forbidden | Usuário autenticado mas sem permissão para o recurso |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Formato de dados inválido |
| 500 | Internal Server Error | Erro no servidor |
| 503 | Service Unavailable | Banco de dados desconectado |

---

## Sistema de Moderação de Conteúdo

A API utiliza **Azure OpenAI GPT-4** para moderação automática de conteúdo antes de salvar no banco de dados.

**Endpoints com Moderação Ativa:**
- `POST /api/threads` - Modera título e descrição
- `PUT /api/threads/<id>` - Modera campos atualizados
- `POST /api/threads/<id>/posts` - Modera conteúdo do post
- `PUT /api/posts/<id>` - Modera conteúdo atualizado

**Categorias Verificadas:**
- ❌ Conteúdo sexual/explícito
- ❌ Violência/ameaças
- ❌ Discriminação/racismo/discurso de ódio
- ❌ Assédio
- ❌ Automutilação/suicídio
- ❌ Golpes/fraudes
- ❌ Spam
- ❌ Linguagem ofensiva/profanação

**Configuração da IA:**
- Modelo: GPT-4 (gpt-4_MarcioJunior_PECC)
- Endpoint: Azure OpenAI
- Temperature: 0.0 (determinístico)
- Max Tokens: 200

**Resposta em Caso de Conteúdo Inapropriado:**
```json
{
  "error": "Conteúdo bloqueado: discrimination - detected discriminatory content"
}
```

**Comportamento em Caso de Falha da IA:**
Se a API de moderação falhar (timeout, erro de rede, etc.), o conteúdo **é permitido** (fail-open approach) para não bloquear o usuário.

---

## Variáveis de Ambiente

Configure estas variáveis no arquivo `.env`:

```env
# Frontend URL
REACT_APP_URL=http://localhost:3000

# Flask Configuration
FLASK_APP=main.py
FLASK_ENV=development

# MongoDB
MONGODB_URI=mongodb://localhost:27017/forum_db
# OU para MongoDB Atlas:
# MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/forum_db

# JWT
JWT_SECRET_KEY=sua-chave-secreta-jwt-super-segura

# API
BASE_URL=http://localhost:5000

# Email (SMTP)
EMAIL=seu-email@gmail.com
EMAIL_PASS=sua-senha-de-app-gmail

# Azure OpenAI (Moderação de Conteúdo)
AZURE_OPENAI_API_KEY=sua-chave-azure-api
```

**Observações:**
- `EMAIL_PASS` deve ser uma "App Password" do Gmail, não a senha normal
- `JWT_SECRET_KEY` deve ser uma string aleatória longa e segura
- `AZURE_OPENAI_API_KEY` é necessário para moderação de conteúdo funcionar

---

## Resumo de Endpoints

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| **AUTENTICAÇÃO** |
| POST | `/api/auth/register` | ❌ | Registrar novo usuário |
| POST | `/api/auth/verify-email` | ❌ | Verificar email com token |
| POST | `/api/auth/resend-verification` | ❌ | Reenviar email de verificação |
| POST | `/api/auth/login` | ❌ | Login e obter JWT token |
| GET | `/api/auth/me` | ✅ | Obter usuário atual |
| **THREADS** |
| GET | `/api/threads` | ✅ | Listar threads (com filtros) |
| POST | `/api/threads` | ✅ | Criar thread |
| GET | `/api/threads/<id>` | ✅ | Obter thread com posts |
| PUT | `/api/threads/<id>` | ✅ | Atualizar thread (autor apenas) |
| DELETE | `/api/threads/<id>` | ✅ | Deletar thread (autor apenas) |
| **POSTS** |
| POST | `/api/threads/<id>/posts` | ✅ | Criar post em thread |
| GET | `/api/posts/<id>` | ✅ | Obter post específico |
| PUT | `/api/posts/<id>` | ✅ | Atualizar post (autor apenas) |
| DELETE | `/api/posts/<id>` | ✅ | Deletar post (autor apenas) |
| **VOTAÇÃO** |
| POST | `/api/<type>/<id>/upvote` | ✅ | Dar upvote (toggle) |
| POST | `/api/<type>/<id>/downvote` | ✅ | Dar downvote (toggle) |
| **PINNING** |
| POST | `/api/posts/<id>/pin` | ✅ | Fixar post (dono thread) |
| DELETE | `/api/posts/<id>/pin` | ✅ | Desfixar post (dono thread) |
| **BUSCA E FILTROS** |
| GET | `/api/filters/config` | ✅ | Obter config completa filtros |
| GET | `/api/filters/<type>` | ✅ | Obter opções de filtro |
| GET | `/api/search/threads` | ✅ | Buscar threads por título |
| **DENÚNCIAS** |
| POST | `/api/reports` | ✅ | Criar denúncia |
| GET | `/api/reports` | ✅ | Listar todas denúncias |
| GET | `/api/reports/<id>` | ✅ | Obter denúncia específica |
| **HEALTH CHECK** |
| GET | `/health` | ✅ | Health check simples |
| GET | `/health/detailed` | ✅ | Health check detalhado |
| **ROOT** |
| GET | `/` | ❌ | Índice da API |

---

## Exemplo de Fluxo Completo

### 1. Registrar e Autenticar

```typescript
// 1. Registrar usuário
const registerResponse = await fetch('http://localhost:5000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'joao.silva@al.insper.edu.br',
    password: 'senhaSegura123!'
  })
});
// Response: { message: "Usuario registrado, email de verificação enviado!" }

// 2. Verificar email (usar token recebido por email)
const verifyResponse = await fetch('http://localhost:5000/api/auth/verify-email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    authToken: 'token-recebido-no-email'
  })
});
// Response: { message: "Email verificado com sucesso!" }

// 3. Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'joao.silva@al.insper.edu.br',
    password: 'senhaSegura123!'
  })
});

const { access_token } = await loginResponse.json();
// access_token válido por 1 hora
```

### 2. Buscar Filtros e Criar Thread

```typescript
// 4. Obter opções de filtros
const filtersResponse = await fetch('http://localhost:5000/api/filters/config', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
const filters = await filtersResponse.json();
// Mostra semestres, cursos e matérias disponíveis

// 5. Criar thread
const threadResponse = await fetch('http://localhost:5000/api/threads', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Como implementar autenticação JWT em Flask?',
    description: 'Estou desenvolvendo uma API REST e preciso de ajuda',
    semester: 3,
    courses: ['cc'],
    subjects: ['Programação Eficaz']
  })
});

const thread = await threadResponse.json();
// thread.id, thread.title, etc.
```

### 3. Criar Post e Votar

```typescript
// 6. Criar post na thread
const postResponse = await fetch(`http://localhost:5000/api/threads/${thread.id}/posts`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Você pode usar Flask-JWT-Extended! Aqui está um exemplo...'
  })
});

const post = await postResponse.json();

// 7. Dar upvote no post
const upvoteResponse = await fetch(`http://localhost:5000/api/posts/${post.id}/upvote`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const voteResult = await upvoteResponse.json();
// { message: "posts upvoted successfully", score: 1 }
```

### 4. Buscar e Denunciar

```typescript
// 8. Buscar threads
const searchResponse = await fetch(
  'http://localhost:5000/api/search/threads?q=JWT&semester=3&courses=cc',
  {
    headers: {
      'Authorization': `Bearer ${access_token}`
    }
  }
);

const searchResults = await searchResponse.json();
// { query: "JWT", count: 2, results: [...] }

// 9. Denunciar conteúdo inapropriado
const reportResponse = await fetch('http://localhost:5000/api/reports', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content_type: 'post',
    content_id: 'post_id_do_spam',
    report_type: 'spam',
    description: 'Este post é claramente spam comercial'
  })
});

const report = await reportResponse.json();
// { message: "Report created successfully", id: "...", status: "pending" }
```

---

## Notas Importantes

### 1. Timezone
- Todos os timestamps são armazenados em **UTC** no MongoDB
- Timestamps são retornados no timezone de **Brasília** (America/Sao_Paulo)
- Formato: ISO 8601 (ex: `2025-01-15T10:30:00-03:00`)

### 2. Sistema de Votação
- **Toggle-based:** Clicar novamente remove o voto
- Usuários não podem votar no próprio conteúdo
- Mudar de upvote para downvote (ou vice-versa) afeta o score em ±2
- Score = total de upvotes - total de downvotes
- Votos são anônimos

### 3. Moderação de Conteúdo
- Usa Azure OpenAI GPT-4
- **Fail-open approach:** Se a IA falhar, conteúdo é permitido
- Aplica-se a: títulos de threads, descrições e conteúdo de posts
- Verifica 8 categorias de conteúdo inapropriado

### 4. Email e Tokens
- Token de verificação de email: **1 hora** de validade
- JWT access token: **1 hora** de validade
- Tokens de verificação só podem ser usados uma vez
- Emails enviados via Gmail SMTP

### 5. Domínio de Email
- Apenas emails `@insper.edu.br` e `@al.insper.edu.br` são aceitos
- Username é extraído automaticamente (parte antes do @)

### 6. Autorização
- **Threads/Posts:** Apenas autor pode editar/deletar
- **Pin Posts:** Apenas dono da thread pode fixar/desfixar
- **Reports:** Usuário não pode denunciar o mesmo conteúdo duas vezes

### 7. Cursos e Matérias
- **9 cursos disponíveis:** CC, ADM, ENG (4 tipos), Direito, Medicina, Psicologia
- **Matérias organizadas por:** Curso → Semestre → Lista de matérias
- **Matérias padrão:** Disponíveis para todos (Matemática Geral, Português, etc.)
- **Busca de matérias:** Case-insensitive, busca por substring

### 8. Ordenação
- **Threads:** Por score (desc), depois por data de criação
- **Posts:** Fixados primeiro, depois por score, depois por data
- **Reports:** Por data de criação (mais recentes primeiro)

### 9. Limites de Caracteres
- Título de thread: **200 caracteres**
- Descrição de thread: **500 caracteres**
- Conteúdo de post: **sem limite explícito**
- Descrição de denúncia: **500 caracteres**

### 10. IDs
- MongoDB ObjectId format (24 caracteres hexadecimais)
- Exemplo: `507f1f77bcf86cd799439011`

---

## Documentação Técnica

**Versão da API:** 1.0.0
**Framework:** Flask 2.3.3
**Database:** MongoDB
**Python:** 3.13
**Última Atualização:** 2025-01-15

**Repositório:** [insper-classroom/20252-progeficaz-projeto-final-backend-fevereiro-backend]

**Contato:** Em caso de dúvidas ou problemas, abra uma issue no repositório.

---

## Changelog

### Version 1.0.0 (2025-01-15)
- ✅ Sistema de autenticação com JWT
- ✅ Verificação de email obrigatória
- ✅ CRUD completo de threads e posts
- ✅ Sistema de votação (upvote/downvote)
- ✅ Sistema de pinning de posts
- ✅ Filtros por semestre, curso e matéria
- ✅ Busca de threads por título
- ✅ Moderação automática com Azure OpenAI
- ✅ Sistema de denúncias com 7 categorias
- ✅ Health checks (simples e detalhado)
- ✅ 9 cursos disponíveis
- ✅ Matérias organizadas por curso/semestre

---

**FIM DA DOCUMENTAÇÃO**
