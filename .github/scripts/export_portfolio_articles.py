"""Export committed Knowledge/Projects Markdown as a public portfolio feed."""
import hashlib
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

REPO = 'c-lydia/dclab_docs'
SITE = 'https://chheng-lydiya-portfolio.vercel.app'
ROOTS = ('04 Knowledge/', '02 Projects/')

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def eligible(path):
    parts = Path(path).parts
    return (path.startswith(ROOTS) and path.lower().endswith('.md')
            and not path.lower().endswith('.excalidraw.md')
            and not any(p.startswith('.') or p.lower() in ('img', 'images', 'attachments') for p in parts)
            and Path(path).stem.lower() not in ('readme', 'index', 'untitled', 'agents'))

def slug(path):
    title = re.sub(r'[^a-z0-9]+', '-', Path(path).stem.lower()).strip('-')[:90] or 'note'
    return f'dclab-{title}-{hashlib.sha256(path.encode()).hexdigest()[:8]}'

def metadata(text):
    """Small optional frontmatter subset: scalar fields and inline tag lists."""
    match = re.match(r'\A---\s*\n(.*?)\n---\s*\n', text, re.S)
    if not match:
        return {}, text
    meta = {}
    for line in match[1].splitlines():
        field = re.match(r'^(title|excerpt|summary|tags|draft|publish):\s*(.*?)\s*$', line)
        if field:
            meta[field[1]] = field[2].strip('\"\'')
    return meta, text[match.end():]

def resolve(target, source, files):
    target = unquote(target)
    local = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
    for candidate in (local, target, local + '.md', target + '.md'):
        if candidate in files:
            return candidate
    matches = [p for p in files if Path(p).name == target or Path(p).stem == target]
    nearby = [p for p in matches if p.startswith(posixpath.dirname(source) + '/')]
    if len(nearby) == 1:
        return nearby[0]
    return matches[0] if len(matches) == 1 else None

def convert_links(body, source, files, published, revision):
    def link(target, label, image=False):
        target = target.strip().strip('<>')
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith(('#', '//')):
            return f'{"!" if image else ""}[{label}]({target})'
        file = resolve(parsed.path, source, files)
        if not file:
            # Keep missing note references readable; don't emit broken image requests.
            return label
        if file in published and not image:
            href = f'{SITE}/#/articles/{slug(file)}'
        elif image and Path(file).suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'):
            href = f'https://raw.githubusercontent.com/{REPO}/{revision}/{quote(file)}'
        else:
            href = f'https://github.com/{REPO}/blob/{revision}/{quote(file)}'
            image = False
        if parsed.fragment and file not in published:
            href += '#' + quote(parsed.fragment)
        return f'{"!" if image else ""}[{label.replace("]", "")}]({href})'
    def transform(part):
        # Convert Markdown relative assets first, then Obsidian wiki links/embeds.
        part = re.sub(r'(!?)\[([^\]\n]*)\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)',
                      lambda m: link(m[3], m[2], bool(m[1])), part)
        def wiki(m):
            target, _, alias = m[2].partition('|')
            label = alias if alias and not re.fullmatch(r'\d+(x\d+)?', alias) else Path(target.split('#')[0]).stem
            return link(target, label, bool(m[1]))
        return re.sub(r'(!?)\[\[([^\]\n]+)\]\]', wiki, part)
    # Never rewrite code examples, including inline code and fenced blocks.
    chunks = re.split(r'(```[^\n]*\n.*?^```[^\n]*$|~~~[^\n]*\n.*?^~~~[^\n]*$|`[^`\n]+`)', body, flags=re.M | re.S)
    return ''.join(chunk if i % 2 else transform(chunk) for i, chunk in enumerate(chunks))

def excerpt(body):
    text = re.sub(r'```.*?```|~~~.*?~~~', '', body, flags=re.S)
    text = re.sub(r'!\[.*?\]\(.*?\)|!\[\[.*?\]\]', '', text)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.lstrip().startswith(('#', 'By:', '|'))]
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', paragraphs[0] if paragraphs else '')
    text = re.sub(r'[*_`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:237].rsplit(' ', 1)[0] + '…' if len(text) > 240 else text

def build_feed():
    files = set(subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')) - {''}
    revision = git('rev-parse', 'HEAD')
    docs = {}
    for path in sorted(files):
        if not eligible(path):
            continue
        meta, body = metadata(Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n'))
        if meta.get('draft', '').lower() == 'true' or meta.get('publish', '').lower() == 'false' or not body.strip():
            continue
        docs[path] = (meta, body)
    articles = []
    for path, (meta, body) in docs.items():
        heading = re.search(r'^# (.+)$', body, re.M)
        title = meta.get('title') or (heading[1] if heading else Path(path).stem)
        if heading and heading.start() == 0:
            body = body[heading.end():].lstrip()
        dates = git('log', '--follow', '--format=%cI', '--', path).splitlines()
        tags = [t.strip(' \"\'') for t in meta.get('tags', '').strip('[]').split(',') if t.strip()]
        articles.append({
            'id': 'github:' + path, 'slug': slug(path), 'title': title,
            'excerpt': meta.get('excerpt') or meta.get('summary') or excerpt(body),
            'tags': tags or ['DCLab', 'Projects' if path.startswith('02 Projects/') else 'Knowledge'],
            'body': convert_links(body, path, files, docs, revision),
            'publishedAt': dates[-1] if dates else None, 'updatedAt': dates[0] if dates else None,
            'source': 'github', 'sourceUrl': f'https://github.com/{REPO}/blob/main/{quote(path)}',
        })
    articles.sort(key=lambda a: a['updatedAt'] or '', reverse=True)
    return {'version': 1, 'repository': REPO, 'revision': revision, 'articles': articles}

if __name__ == '__main__':
    output = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/portfolio-articles.json')
    feed = build_feed()
    output.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + '\n')
    print(f'Exported {len(feed["articles"])} articles from committed Knowledge/Projects notes.')
