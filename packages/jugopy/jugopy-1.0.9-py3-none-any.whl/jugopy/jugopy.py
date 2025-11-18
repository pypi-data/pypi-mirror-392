import os
import re
import json
import http.cookies
import random
import string
import urllib.parse
import pymysql
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from wsgiref.simple_server import make_server
from typing import Dict, Any, Optional, Callable, List, Tuple, Union


BASE_DIR = Path.cwd()
PUBLIC_DIR = BASE_DIR / "public"
HTML_DIR = PUBLIC_DIR / "html"

MIME_TYPES = {
    'css': 'text/css',
    'js': 'application/javascript',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'ico': 'image/x-icon',
    'svg': 'image/svg+xml',
    'webp': 'image/webp',
    'woff': 'font/woff',
    'woff2': 'font/woff2',
    'ttf': 'font/ttf',
}

DIRECTORIES = {
    'css': PUBLIC_DIR / 'css',
    'js': PUBLIC_DIR / 'js',
    'png': PUBLIC_DIR / 'images',
    'jpg': PUBLIC_DIR / 'images',
    'jpeg': PUBLIC_DIR / 'images',
    'gif': PUBLIC_DIR / 'images',
    'ico': PUBLIC_DIR / 'images',
    'svg': PUBLIC_DIR / 'images',
    'webp': PUBLIC_DIR / 'images',
    'woff': PUBLIC_DIR / 'fonts',
    'woff2': PUBLIC_DIR / 'fonts',
    'ttf': PUBLIC_DIR / 'fonts',
}

indexHtml = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }
        .emoji {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .info {
            background: rgba(255, 255, 255, 0.2);
            padding: 1rem;
            border-radius: 10px;
            margin-top: 2rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🎉</div>
        <h1>Bienvenue sur {{ title }}</h1>
        <p class="subtitle">Votre application JUGOPY fonctionne parfaitement</p>
        <div class="info">
            <strong>Framework JUGOPY</strong> - Développé avec passion ❤️
        </div>
    </div>
</body>
</html>"""

errorHtml = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ status }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 500px;
        }
        .emoji {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .error-message {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .action {
            margin-top: 2rem;
        }
        .btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.8rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            transition: all 0.3s ease;
            display: inline-block;
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🚨</div>
        <h1>{{ status }}</h1>
        <div class="error-message">{{ error }}</div>
        <div class="action">
            <a href="/" class="btn">Retour à l'accueil</a>
        </div>
    </div>
</body>
</html>"""

ERROR_PAGE = HTML_DIR / 'error.html'
SESSION_FILE = BASE_DIR / 'sessions.json'

TEMPLATE_ENV = Environment(loader=FileSystemLoader(str(HTML_DIR)))

ROUTES = {}
STATIC_CACHE = {}
MIDDLEWARES = []


class JugoColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    LEVEL_COLORS = {
        'INFO': BLUE,
        'SUCCESS': GREEN,
        'WARNING': WARNING,
        'ERROR': FAIL,
        'HEADER': HEADER
    }


def jugoPrint(message: str, level: str = "INFO") -> None:
    color = JugoColors.LEVEL_COLORS.get(level, JugoColors.ENDC)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\t{color}[{timestamp}] {level}: {message}{JugoColors.ENDC}\t")


def getDBConfig():
    import sys
    import inspect
        
    for module_name, module in sys.modules.items():
        if hasattr(module, 'conn_infos'):
            return getattr(module, 'conn_infos')
    
    frame = inspect.currentframe()
    try:
        while frame:
            if 'conn_infos' in frame.f_globals:
                return frame.f_globals['conn_infos']
            frame = frame.f_back
    finally:
        del frame
    
    jugoPrint("⚠️  Configuration DB non trouvée, utilisation des valeurs par défaut", "WARNING")
    return ['localhost', 'root', '', 'default_db']


def jugoServeError(status: str, content: str, startResponse) -> list[bytes]:
    jugoPrint(f"🚨 Erreur serveur: {status} - {content}", "ERROR")
    
    startResponse(status, [('Content-Type', 'text/html')])
    
    if '404' in status:
        user_message = f"Route '{content}' introuvable"
    else:
        user_message = "Erreur interne, veuillez contacter l'administrateur"
    
    try:
        html_content = errorHtml.replace('{{ status }}', status)
        html_content = html_content.replace('{{ error }}', user_message)
        return [html_content.encode('utf-8')]
    except Exception as e:
        jugoPrint(f"Erreur lors du rendu de la page d'erreur: {e}", "ERROR")
        return [f"<h1>{status}</h1><p>{user_message}</p>".encode('utf-8')]


def jugoRoute(path: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        jugoPrint(f"🛣️  Route enregistrée: {path}", "SUCCESS")
        ROUTES[path] = func
        return func
    return decorator


def jugoMiddleware(func):
    MIDDLEWARES.append(func)
    return func


@jugoMiddleware
def logMiddleware(environ):
    jugoPrint(f"📨 {environ['REQUEST_METHOD']} {environ['PATH_INFO']}")


def _isStaticFile(path: str) -> bool:
    filename = path.split('/')[-1]
    return '.' in filename and filename not in ['', '.', '..']


def _getStaticFilePath(filePath: str) -> Optional[Path]:
    filename = filePath.split('/')[-1]
    ext = Path(filename).suffix.lstrip('.')
    
    if not ext or ext not in DIRECTORIES or ext not in MIME_TYPES:
        return None
    
    folder = DIRECTORIES[ext]
    return folder / filename


def _serveStaticFile(filePath: str, startResponse) -> Optional[list[bytes]]:    
    if filePath in STATIC_CACHE:
        ext = Path(filePath).suffix.lstrip('.')
        mimeType = MIME_TYPES.get(ext, 'application/octet-stream')
        startResponse('200 OK', [('Content-Type', mimeType)])
        return [STATIC_CACHE[filePath]]
    
    fullPath = _getStaticFilePath(filePath)
    if not fullPath or not fullPath.exists():
        return None
    
    try:
        with open(fullPath, 'rb') as f:
            content = f.read()
        
        if len(content) < 1024 * 1024:
            STATIC_CACHE[filePath] = content
        
        ext = Path(filePath).suffix.lstrip('.')
        mimeType = MIME_TYPES.get(ext, 'application/octet-stream')
        startResponse('200 OK', [('Content-Type', mimeType)])
        return [content]
    except Exception as e:
        jugoPrint(f"❌ Erreur lecture fichier statique {filePath}: {e}", "ERROR")
        return None


def jugoDispatch(environ, startResponse) -> list[bytes]:
    path = environ.get('PATH_INFO', '/')
        
    for middleware in MIDDLEWARES:
        middleware(environ)
    
    if _isStaticFile(path):
        result = _serveStaticFile(path, startResponse)
        if result:
            jugoPrint(f"✅ Requête statique traitée avec succès: {path}", "SUCCESS")
            return result
        return jugoServeError('500 Internal Server Error', f"Fichier {path} introuvable", startResponse)
    
    handler = ROUTES.get(path)
    if handler:
        try:
            result = handler(environ, startResponse)
            return result
        except Exception as e:
            errorMsg = str(e)
            jugoPrint(f"❌ Erreur dans le handler {handler.__name__}: {errorMsg}", "ERROR")
            return jugoServeError('500 Internal Server Error', errorMsg, startResponse)
    
    jugoPrint(f"❌ Route non trouvée: {path}", "WARNING")
    return jugoServeError('404 Not Found', path, startResponse)


def jugoRender(templateName: str, context: Optional[Dict[str, Any]] = None, startResponse = None) -> list[bytes]:
    context = context or {}
    jugoPrint(f"🎨 Rendu du template: {templateName}", "INFO")
    
    try:
        template = TEMPLATE_ENV.get_template(templateName)
        html = template.render(**context)
        startResponse('200 OK', [('Content-Type', 'text/html')])
        jugoPrint(f"✅ Template rendu avec succès: {templateName}", "SUCCESS")
        return [html.encode('utf-8')]
    except Exception as e:
        errorMsg = f"Erreur rendu: {e}"
        jugoPrint(f"❌ {errorMsg}", "ERROR")
        return jugoServeError('500 Internal Server Error', errorMsg, startResponse)


def jugoParsePost(environ) -> Dict[str, Any]:
    jugoPrint("📝 Parsing des données POST...", "INFO")
    
    contentType = environ.get("CONTENT_TYPE", "").lower()
    contentLength = int(environ.get("CONTENT_LENGTH", 0))
    
    if contentLength == 0:
        jugoPrint("📝 Aucune donnée POST", "INFO")
        return {}
    
    body = environ["wsgi.input"].read(contentLength)

    if contentType.startswith("application/x-www-form-urlencoded"):
        data = urllib.parse.parse_qs(body.decode("utf-8"))
        result = {k: v[0] for k, v in data.items()}
        jugoPrint(f"📝 Données POST parsées: {len(result)} champs", "SUCCESS")
        return result

    elif contentType.startswith("multipart/form-data"):
        boundary = contentType.split("boundary=")[-1].strip()
        if not boundary:
            return {}
        data = {}
        parts = body.split(f"--{boundary}".encode())
        for part in parts:
            if b"Content-Disposition" in part:
                try:
                    header, content = part.split(b"\r\n\r\n", 1)
                    content = content.strip(b"\r\n--")
                    nameMatch = re.search(rb'name="([^"]+)"', header)
                    if nameMatch:
                        name = nameMatch.group(1).decode("utf-8")
                        data[name] = content.decode("utf-8", errors="ignore")
                except Exception:
                    continue
        jugoPrint(f"📝 Données multipart parsées: {len(data)} champs", "SUCCESS")
        return data

    jugoPrint("📝 Type de contenu POST non supporté", "WARNING")
    return {}


def jugoSetCookie(environ, name: str, content: Any) -> None:
    jugoPrint(f"🍪 Définition du cookie: {name}", "INFO")
    cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    val = json.dumps(content) if isinstance(content, (dict, list)) else str(content)
    cookies[name] = val
    environ['HTTP_COOKIE'] = '; '.join(f"{k}={v.value}" for k, v in cookies.items())
    jugoPrint(f"✅ Cookie défini: {name}", "SUCCESS")


def jugoGetCookie(environ, name: str) -> Any:
    jugoPrint(f"🍪 Récupération du cookie: {name}", "INFO")
    cookies = http.cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
    if name in cookies:
        val = cookies[name].value
        try:
            result = json.loads(val)
            jugoPrint(f"✅ Cookie trouvé: {name}", "SUCCESS")
            return result
        except json.JSONDecodeError:
            jugoPrint(f"✅ Cookie trouvé (valeur brute): {name}", "SUCCESS")
            return val
    jugoPrint(f"❌ Cookie non trouvé: {name}", "WARNING")
    return None


def jugoGetSession(sessionId: str) -> Dict[str, Any]:
    jugoPrint(f"🔐 Récupération de la session: {sessionId}", "INFO")
    if not SESSION_FILE.exists():
        jugoPrint("❌ Fichier de sessions inexistant", "WARNING")
        return {}
    try:
        with open(SESSION_FILE, 'r') as f:
            sessions = json.load(f)
        
        sessionData = sessions.get(sessionId, {})
        if sessionData.get('expires', 0) < datetime.now().timestamp():
            jugoPrint(f"❌ Session expirée: {sessionId}", "WARNING")
            return {}
        
        jugoPrint(f"✅ Session récupérée: {sessionId}", "SUCCESS")
        return sessionData.get('data', {})
    except Exception as e:
        jugoPrint(f"❌ Erreur lecture session: {e}", "ERROR")
        return {}


def jugoSaveSession(sessionId: str, data: Dict[str, Any], expireHours: int = 24) -> None:
    jugoPrint(f"💾 Sauvegarde session: {sessionId} (expire dans {expireHours}h)", "INFO")
    sessions = {}
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, 'r') as f:
                sessions = json.load(f)
        except Exception as e:
            jugoPrint(f"⚠️  Erreur lecture sessions existantes: {e}", "WARNING")
    
    sessions[sessionId] = {
        'data': data,
        'expires': datetime.now().timestamp() + (expireHours * 3600)
    }
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f)
        jugoPrint(f"✅ Session sauvegardée: {sessionId}", "SUCCESS")
    except Exception as e:
        jugoPrint(f"❌ Erreur sauvegarde session: {e}", "ERROR")


def jugoCrypt(data: Any) -> str:
    jugoPrint(f"🔒 Cryptage des données...", "INFO")
    data = str(data)
    seed = sum((ord(c) + i * 7) * (i + 2) for i, c in enumerate(data))
    random.seed(seed)
    result = ''.join(random.sample(string.ascii_letters + string.digits + "@*-+_!?&$#%^", 10))
    jugoPrint(f"✅ Données cryptées: {result}", "SUCCESS")
    return result


def jugoCsrfToken() -> str:
    jugoPrint("🛡️  Génération token CSRF...", "INFO")
    token = jugoCrypt(str(random.random()))
    jugoPrint(f"✅ Token CSRF généré", "SUCCESS")
    return token


def jugoValidateCsrf(environ, tokenName='csrf_token'):
    jugoPrint("🛡️  Validation token CSRF...", "INFO")
    formData = jugoParsePost(environ)
    sessionId = jugoGetCookie(environ, 'session_id')
    session = jugoGetSession(sessionId) if sessionId else {}
    isValid = formData.get(tokenName) == session.get('csrf_token')
    
    if isValid:
        jugoPrint("✅ Token CSRF valide", "SUCCESS")
    else:
        jugoPrint("❌ Token CSRF invalide", "ERROR")
    
    return isValid


def jugoValidEmail(email: str) -> bool:
    jugoPrint(f"📧 Validation email: {email}", "INFO")
    isValid = re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email) is not None
    
    if isValid:
        jugoPrint("✅ Email valide", "SUCCESS")
    else:
        jugoPrint("❌ Email invalide", "WARNING")
    
    return isValid


def jugoSlugify(text: str) -> str:
    jugoPrint(f"🔤 Slugification: {text}", "INFO")
    text = re.sub(r'[^a-zA-Z0-9-]+', '-', text.lower())
    result = text.strip('-')
    jugoPrint(f"✅ Texte slugifié: {result}", "SUCCESS")
    return result


def jugoRedirect(location: str, startResponse, extraHeaders: Optional[list] = None) -> list[bytes]:
    jugoPrint(f"↪️  Redirection vers: {location}", "INFO")
    headers = [("Location", location)]
    if extraHeaders:
        headers.extend(extraHeaders)
    startResponse('302 Found', headers)
    jugoPrint(f"✅ Redirection effectuée: {location}", "SUCCESS")
    return [b'']


def jugoCors(headers=None):
    jugoPrint("🌐 Configuration CORS...", "INFO")
    corsHeaders = [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]
    if headers:
        corsHeaders.extend(headers)
    jugoPrint("✅ Headers CORS configurés", "SUCCESS")
    return corsHeaders


def connDb() -> pymysql.connections.Connection:
    jugoPrint("🔌 Tentative de connexion à la base de données...", "INFO")
    try:
        db_config = getDBConfig()
        conn = pymysql.connect(
            host=db_config[0],
            user=db_config[1],
            password=db_config[2],
            database=db_config[3]
        )
        jugoPrint(f"✅ Connexion DB réussie: {db_config[3]}", "SUCCESS")
        return conn
    except Exception as e:
        jugoPrint(f"❌ Erreur connexion DB: {e}", "ERROR")
        raise


def runSql(sql: str, params: tuple = None, conn = None) -> Union[List[Dict], int, None]:
    jugoPrint(f"🗃️  Exécution SQL: {sql[:50]}...", "INFO")
    
    if conn is None:
        try:
            conn = connDb()
        except Exception as e:
            jugoPrint(f"❌ Erreur connexion DB dans runSql: {e}", "ERROR")
            return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            
            if sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESC')):
                result = cursor.fetchall()
                columns = [col[0] for col in cursor.description] if cursor.description else []
                final_result = [dict(zip(columns, row)) for row in result]
                jugoPrint(f"✅ SQL SELECT réussi: {len(final_result)} lignes", "SUCCESS")
                return final_result
            else:
                conn.commit()
                rowcount = cursor.rowcount
                jugoPrint(f"✅ SQL exécuté: {rowcount} lignes affectées", "SUCCESS")
                return rowcount
                
    except Exception as e:
        jugoPrint(f"❌ Erreur SQL: {e}", "ERROR")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()
            jugoPrint("🔌 Connexion DB fermée", "INFO")


def jugoRun(app, host: str = '127.0.0.1', port: int = 8080) -> None:
    jugoPrint("🚀 Démarrage de l'application JUGOPY...", "HEADER")
    db_config = getDBConfig()
    jugoPrint(f"🔧 Configuration DB: {db_config[3]}", "INFO")
    jugoPrint(f"🌐 Serveur démarré sur http://{host}:{port}", "SUCCESS")
    jugoPrint("📍 Press Ctrl+C to stop the server", "INFO")
    
    with make_server(host, port, app) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            jugoPrint("🛑 Serveur arrêté par l'utilisateur", "WARNING")


def jugoCreateApp(appName: str, inRoot: bool = False) -> None:
    baseDir = Path.cwd() if inRoot else Path.cwd() / appName

    if baseDir.exists() and not inRoot:
        print(f"❌ Le dossier '{appName}' existe déjà.")
        return

    structure = [
        baseDir / "public" / "html",
        baseDir / "public" / "css",
        baseDir / "public" / "js",
        baseDir / "public" / "images",
        baseDir / "public" / "fonts",
        baseDir / "core",
    ]

    for path in structure:
        path.mkdir(parents=True, exist_ok=True)

    (baseDir / "public" / "html" / "index.html").write_text(indexHtml, encoding='utf-8')
    (baseDir / "public" / "html" / "error.html").write_text(errorHtml, encoding='utf-8')
    
    app_content = f"""from jugopy import *

# Configuration DB
conn_infos = ['localhost', 'root', '', '{appName.lower()}_db']

@jugoRoute('/')
def index(environ, startResponse):
    return jugoRender('index.html', {{'title': '{appName.capitalize()}'}}, startResponse)

if __name__ == "__main__":
    jugoRun(jugoDispatch)
"""
    
    (baseDir / "app.py").write_text(app_content, encoding='utf-8')

    print(f"✅ Projet '{appName}' créé avec succès dans : {baseDir}")
    print("👉 Pour démarrer :")
    print(f"   cd {appName}" if not inRoot else "   (déjà dans le dossier)")
    print("   python app.py")
