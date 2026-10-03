#!/usr/bin/env python3
"""Build public summaries and a short preview from a PRIVATE sibling archive.
The full transcription, source evidence quotes and raw inventory are never copied.
Standard library only; this script does not publish anything or access credentials.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
import argparse, collections, hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--private-source', type=Path, default=ROOT.parent / 'riposte-accompagnement/data')
args = parser.parse_args()
private = args.private_source
raw = json.loads((private / 'sources.json').read_text())
md_bytes = (private / 'transcription.md').read_bytes()
srt = (private / 'sous-titres.srt').read_text()

def esc(value):
    return escape(str(value or ''), quote=True)

def safe_url(value):
    if not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('Unsupported source URL')
    return value

def stamp(seconds):
    total = int(seconds)
    return f'{total // 3600:02d}:{total // 60 % 60:02d}:{total % 60:02d}'

def youtube(seconds):
    return f'https://www.youtube.com/watch?v=kKOcQM1eynE&t={int(seconds)}'

labels = {'article-read': 'Article consulté pendant la recherche initiale',
          'search-only': 'Correspondance repérée via recherche/RSS : texte intégral non consulté',
          'unresolved': 'Correspondance non résolue'}
public = []
for item in raw:
    out = {key: item[key] for key in ['title', 'seconds', 'type', 'summary', 'notes']}
    out['sources'] = []
    for source in item.get('sources', []):
        out['sources'].append({key: source.get(key) for key in ['title', 'publisher', 'date', 'verification']}
                              | {'url': safe_url(source.get('url'))})
    public.append(out)
counts = dict(collections.Counter(item['type'] for item in public))
associated = sum(any(s['url'] for s in item['sources']) for item in public)
read = sum(any(s['verification'] == 'article-read' for s in item['sources']) for item in public)
metadata = {
    'file': 'transcription.md', 'sha256': hashlib.sha256(md_bytes).hexdigest(),
    'bytes': len(md_bytes), 'segments': len(re.findall(r'^\d+\n\d{2}:\d{2}:\d{2},\d{3} -->', srt, re.M)),
    'episode_duration_seconds': 5976.769887,
    'scope': 'Fichier Markdown révisé complet conservé en privé ; encodage UTF-8 et octets exacts, sans normalisation.',
    'limitation': 'Engagement sur une version : cette empreinte seule ne prouve ni la complétude, ni l’exactitude, ni l’existence publique du fichier.'
}

def source_html(source):
    label = labels.get(source['verification'], 'Statut non établi')
    if not source['url']:
        return f'<li><span class="muted">{esc(label)}</span></li>'
    return (f'<li><a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(source["title"] or source["url"])} ↗</a><br>'
            f'<span class="muted">{esc(source["publisher"])} · {esc(source["date"] or "date non établie")} · {esc(label)}</span></li>')

parts = []
review = ['# La Riposte — revue de presse et références associées', '',
          'Synthèses personnelles non officielles pour l’émission du 28 septembre 2026.',
          'Les sources associées ne sont pas nécessairement celles de l’équipe. Les synthèses résument les sujets repérés : elles ne certifient pas les affirmations de l’émission.',
          f'{len(public)} entrées : {counts}. {associated} entrées avec articles associés, dont {read} avec un article consulté.',
          'Les correspondances recherche/RSS ne valent pas lecture du texte intégral. Les sources de contexte et les incertitudes restent indiquées.', '']
for category, heading in [('actualité', 'Actualités'), ('contexte', 'Références de contexte'), ('anecdote / promotion', 'Anecdotes et promotions')]:
    cards = []
    review += [f'## {heading}', '']
    for number, item in enumerate(public, 1):
        if item['type'] != category:
            continue
        time = stamp(item['seconds'])
        cards.append(f'<article class="card" id="topic-{number}"><h3>{esc(item["title"])}</h3>'
                     f'<p><a href="{esc(youtube(item["seconds"]))}" target="_blank" rel="noopener noreferrer">{time} sur YouTube ↗</a></p>'
                     f'<p>{esc(item["summary"])}</p><ul>{"".join(source_html(s) for s in item["sources"])}</ul>'
                     f'<p class="note">{esc(item["notes"])}</p></article>')
        review += [f'### {time} — {item["title"]}', '', item['summary'], '', f'Passage officiel : {youtube(item["seconds"])}', '']
        for source in item['sources']:
            review.append(f'- {source["title"] or "Source non identifiée"} — {source["publisher"] or ""} — {source["date"] or "date non établie"} — {labels.get(source["verification"], "Statut non établi")}')
            if source['url']:
                review.append('  ' + source['url'])
        review += ['', 'Limites et contexte : ' + item['notes'], '']
    parts.append(f'<section><h2>{heading} ({counts[category]})</h2>{"".join(cards)}</section>')

excerpt = []
for label, line in re.findall(r'^\*\*\[([^\]]+)\]\*\* (.*)$', md_bytes.decode(), re.M):
    h, m, s = label.replace(',', '.').split(':')
    seconds = int(h) * 3600 + int(m) * 60 + float(s)
    if 42 <= seconds < 51.5:
        excerpt.append(f'<p class="cue"><span class="time"><a href="{esc(youtube(seconds))}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a></span><span>{esc(line)}</span></p>')

page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'none'"><meta name="description" content="Revue de presse personnelle et aperçu limité d’une proposition d’accompagnement de La Riposte, par un auditeur."><title>La Riposte — revue de presse et aperçu non officiel</title><link rel="stylesheet" href="assets/style.css"></head><body>
<header><p class="badge">Projet personnel non officiel · proposition à l’équipe</p><h1>Retrouver les références de La Riposte</h1><p>Revue de presse et aperçu d’une transcription horodatée de l’émission du 28 septembre 2026.</p><p class="note">Thomas · <a href="mailto:thomas@codethelaw.eu">thomas@codethelaw.eu</a>. Aucun partenariat ni validation de Radio Nova ou de l’équipe n’est présumé.</p><p><a class="button" href="https://www.youtube.com/watch?v=kKOcQM1eynE" target="_blank" rel="noopener noreferrer">Regarder la vidéo officielle sur YouTube ↗</a></p></header>
<nav aria-label="Navigation"><a href="#proposal">La proposition</a><a href="#excerpt">Court extrait</a><a href="#version">Version complète</a><a href="#sources">Revue de presse</a><a href="#contact">Contact et limites</a></nav><main>
<section id="proposal"><h2>Un complément facultatif</h2><p>J’aime beaucoup La Riposte. La proposition principale est une <strong>revue de presse semi-automatisée</strong> : repérer les sujets évoqués, retrouver des articles associés et les relier aux passages de l’émission. Ce premier essai vise à explorer avec l’équipe ce qui pourrait lui être utile, pas à créer un projet parallèle.</p><ul><li>Une aide au repérage et à l’organisation des références, avec vérification éditoriale nécessaire.</li><li>Une transcription horodatée et des sous-titres proposés en privé comme outils de travail : retrouver des passages et préparer une base de sous-titres à corriger.</li><li>Un éventuel lecteur synchronisé utilisant uniquement la vidéo YouTube officielle.</li></ul><p class="warning">Cette page ne diffuse aucune vidéo, aucun audio, aucune transcription intégrale ni sous-titres complets. La transcription intégrale n’est pas destinée à une publication indépendante ici. La revue de presse est une synthèse personnelle non officielle, sans reproduction intégrale des articles.</p></section>
<section id="excerpt"><h2>Un court exemple de transcription horodatée</h2><p class="note">Environ dix secondes de présentation. Les liens ouvrent la vidéo officielle au passage correspondant.</p>{''.join(excerpt)}</section>
<section id="version"><h2>Une transcription complète comme outil de travail pour l’équipe</h2><p>Le fichier révisé couvre l’épisode d’environ 1 h 39 min et comprend {metadata['segments']:,} segments de sous-titres. Il reste en cours de relecture, sans validation intégrale à l’écoute.</p><p>Empreinte SHA-256 du Markdown complet ({metadata['bytes']:,} octets) :</p><p class="note"><code>{metadata['sha256']}</code></p><p class="note">Cette empreinte engage sur une version précise et permettra une comparaison si le fichier est ensuite partagé. Elle ne prouve pas à elle seule la complétude, l’exactitude ou l’existence du fichier. Ce n’est pas une preuve zero-knowledge. Aucune API publique ne distribue la transcription par morceaux.</p><p><a href="data/version-transcription.json" download>Métadonnées de version (.json)</a></p></section>
<section id="sources"><h2>Revue de presse et références associées</h2><p>{len(public)} entrées : {counts['actualité']} actualités, {counts['contexte']} références de contexte, {counts['anecdote / promotion']} anecdotes/promotions. {associated} entrées ont des articles associés ; {read} ont au moins un article consulté lors de la recherche initiale.</p><p class="note">Ces sources ne sont pas nécessairement celles de l’équipe. Les synthèses décrivent les sujets évoqués, sans certifier les affirmations de l’émission. Une source de contexte n’établit pas tous les détails du propos. Les correspondances recherche/RSS ne valent pas lecture du texte intégral. L’inventaire ne garantit ni exhaustivité ni attribution exacte.</p><p><a href="data/revue-de-presse.md" download>Revue de presse (.md)</a> · <a href="data/sources.json" download>Inventaire public sans citations détaillées (.json)</a></p></section>{''.join(parts)}
<section id="contact"><h2>Améliorer ce prototype ensemble</h2><p>La transcription a été produite avec l’aide de Whisper et de LLM, puis partiellement corrigée à l’écoute. Des erreurs et incertitudes subsistent. Il ne s’agit pas d’une transcription officiellement validée ni d’un fact-checking de l’émission.</p><p>Les retours et demandes de correction ou de retrait sont bienvenus. Les droits sur les propos et les articles restent ceux de leurs ayants droit.</p><p><a href="mailto:thomas@codethelaw.eu">Contacter Thomas ↗</a> · <a href="https://github.com/tsua0002/riposte-apercu" target="_blank" rel="noopener noreferrer">Inspecter le code ↗</a></p><p class="note">Page statique : aucun JavaScript, lecteur embarqué, formulaire, téléchargement automatique ou outil d’analyse d’audience. L’hébergeur peut conserver des journaux techniques ; les services externes ont leurs propres politiques. Cela ne constitue pas une certification de sécurité.</p></section>
</main><footer><p>Aperçu personnel non officiel. La transcription intégrale et le lecteur vidéo ne sont pas distribués ici.</p></footer></body></html>'''
(ROOT / 'data').mkdir(exist_ok=True)
(ROOT / 'index.html').write_text(page)
(ROOT / 'data/sources.json').write_text(json.dumps(public, ensure_ascii=False, indent=2))
(ROOT / 'data/version-transcription.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
(ROOT / 'data/revue-de-presse.md').write_text('\n'.join(review))
print(f'Built public preview: {len(public)} topics, {len(excerpt)} short cues; no full transcript or media.')
