#!/usr/bin/env python3
"""Build public summaries and a short preview from a PRIVATE sibling archive.
The full transcription, source evidence quotes and raw inventory are never copied.
Standard library only; this script does not publish anything or access credentials.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, quote
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

labels = {'article-read': 'Article consulté',
          'search-only': 'Article repéré · texte intégral non consulté',
          'unresolved': 'Source non identifiée'}
editorial = json.loads((ROOT / 'data/editorial-copy.json').read_text())
if len(editorial) != len(raw):
    raise ValueError('Editorial copy must cover the complete source inventory')
public = []
for number, item in enumerate(raw, 1):
    copy = editorial[number - 1]
    if (copy['id'] != f'topic-{number}' or copy['original_title'] != item['title']
            or copy['seconds'] != item['seconds']):
        raise ValueError(f'Editorial/source mismatch for topic-{number}; review before rebuilding')
    out = {key: item[key] for key in ['title', 'seconds', 'type', 'summary', 'notes']}
    out.update({key: copy[key] for key in ['title', 'summary', 'notes']})
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

def french_number(value):
    return f'{value:,}'.replace(',', '\u202f')

def readable_date(value):
    if not value:
        return 'Date non identifiée'
    try:
        from datetime import date
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        return str(value)
    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
              'août', 'septembre', 'octobre', 'novembre', 'décembre']
    return f'{parsed.day} {months[parsed.month - 1]} {parsed.year}'

def source_html(source):
    label = labels.get(source['verification'], 'Statut non établi')
    if not source['url']:
        return f'<li><span class="source-meta">{esc(label)}</span></li>'
    return (f'<li><a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(source["title"] or source["url"])} ↗</a><br>'
            f'<span class="source-meta">{esc(source["publisher"])} · {esc(readable_date(source["date"]))} · {esc(label)}</span></li>')

parts = []
review = ['# La Riposte — revue de presse et références associées', '',
          'Projet personnel non officiel pour l’émission du 28 septembre 2026.',
          'Une base à relire, pas un fact-checking de l’émission. Les articles associés ne sont pas nécessairement ceux utilisés par l’équipe.',
          f'{len(public)} sujets repérés : {counts["actualité"]} sujets d’actualité, {counts["contexte"]} références de contexte et {counts["anecdote / promotion"]} anecdotes ou annonces.',
          f'{associated} sujets ont un article associé. Pour {read} sujets, au moins un article a été consulté pendant la recherche ; cela ne signifie pas que ces sujets sont vérifiés.',
          '« Article repéré » signifie que son titre et ses informations de publication ont été trouvés, sans lecture du texte intégral. Les dates issues de ces résultats n’ont pas toutes été contrôlées sur le site de l’éditeur.',
          'La liste peut être incomplète. Les attributions incertaines et les correspondances partielles restent signalées.', '']
for category, heading, slug in [('actualité', 'Sujets d’actualité', 'actualites'), ('contexte', 'Références de contexte', 'contextes'), ('anecdote / promotion', 'Anecdotes et annonces', 'anecdotes')]:
    cards = []
    review += [f'## {heading}', '']
    for number, item in enumerate(public, 1):
        if item['type'] != category:
            continue
        time = stamp(item['seconds'])
        cards.append(f'<article class="card" id="topic-{number}" data-category="{esc(category)}" data-seconds="{item["seconds"]}" tabindex="-1"><div class="topic-time"><a href="{esc(youtube(item["seconds"]))}" target="_blank" rel="noopener noreferrer" aria-label="Ouvrir le passage à {time} sur YouTube">{time} ↗</a><span class="topic-kind">{esc(category)}</span></div><div class="topic-body"><h3>{esc(item["title"])}</h3>'
                     f'<p>{esc(item["summary"])}</p><ul>{"".join(source_html(s) for s in item["sources"])}</ul>'
                     f'<details class="source-details"><summary>Notes de recherche</summary><p>{esc(item["notes"])}</p></details>'
                     f'<div class="topic-actions"><a href="#topic-{number}" class="permalink" aria-label="Lien direct : {esc(item["title"])}">Ouvrir ce sujet</a>'
                     f'<button type="button" class="copy-link" hidden aria-label="Copier le lien : {esc(item["title"])}">Copier le lien</button>'
                     f'<a href="mailto:thomas@codethelaw.eu?subject={quote("Correction — " + item["title"])}&amp;body={quote("Sujet : " + item["title"] + chr(10) + "Passage : " + time + chr(10) + "Correction proposée : " )}">Proposer une correction</a></div></div></article>')
        review += [f'### {time} — {item["title"]}', '', item['summary'], '', f'Passage officiel : {youtube(item["seconds"])}', '']
        for source in item['sources']:
            review.append(f'- {source["title"] or "Source non identifiée"} — {source["publisher"] or ""} — {readable_date(source["date"])} — {labels.get(source["verification"], "Statut non établi")}')
            if source['url']:
                review.append('  ' + source['url'])
        review += ['', 'Limites et contexte : ' + item['notes'], '']
    parts.append(f'<section class="topic-section" id="{slug}"><h2>{heading} <span class="section-count">{counts[category]}</span></h2>{"".join(cards)}</section>')

def srt_seconds(value):
    h, m, s = value.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)
ends = {srt_seconds(start): srt_seconds(end) for start, end in re.findall(
    r'^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', srt, re.M)}
excerpt = []
for label, line in re.findall(r'^\*\*\[([^\]]+)\]\*\* (.*)$', md_bytes.decode(), re.M):
    h, m, s = label.replace(',', '.').split(':')
    seconds = int(h) * 3600 + int(m) * 60 + float(s)
    if 42 <= seconds < 51.5:
        end = ends[seconds]
        excerpt.append(f'<p class="cue" data-start="{seconds}" data-end="{end}"><span class="time"><a href="{esc(youtube(seconds))}" target="_blank" rel="noopener noreferrer" aria-label="Lire le passage à {esc(label)}">{esc(label)} ↗</a></span><span>{esc(line)}</span></p>')

class NoteHints(HTMLParser):
    """Replace every note/muted element, preserving its content and live IDs."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []; self.stack = []; self.count = 0
    def handle_starttag(self, tag, attrs):
        is_note = tag in ('p', 'span') and bool(set(dict(attrs).get('class', '').split()) & {'hint-note'})
        if is_note:
            self.count += 1
            self.output.append(f'<span class="info-hint"><button class="info-button" type="button" aria-label="Informations complémentaires" aria-expanded="false" aria-describedby="info-{self.count}"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v1"/></svg></button><span id="info-{self.count}" class="info-tooltip" role="tooltip"><span ' + ' '.join(f'{key}="{esc(value)}"' if value is not None else key for key,value in attrs) + '>')
        else:
            self.output.append(self.get_starttag_text())
        if tag not in ('meta','link','input','br','hr','img','source','track','wbr','area','base','col','embed','param'):
            self.stack.append((tag,is_note))
    def handle_endtag(self, tag):
        original, is_note = self.stack.pop()
        if original != tag: raise ValueError('Unexpected HTML nesting')
        self.output.append('</span></span></span>' if is_note else f'</{tag}>')
    def handle_data(self, data): self.output.append(data)
    def handle_entityref(self, name): self.output.append('&'+name+';')
    def handle_charref(self, name): self.output.append('&#'+name+';')
    def handle_decl(self, decl): self.output.append('<!'+decl+'>')

asset_version = hashlib.sha256(b''.join((ROOT / 'assets' / name).read_bytes()
    for name in ['style.css', 'youtube-demo.mjs', 'demo-core.mjs', 'hints.mjs', 'explorer.mjs', 'explorer-core.mjs'])).hexdigest()[:12]
page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' https://www.youtube.com; frame-src https://www.youtube-nocookie.com; style-src 'self'; font-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="description" content="Revue de presse personnelle et aperçu limité d’une proposition d’accompagnement de La Riposte, par un auditeur."><title>La Riposte — revue de presse et aperçu non officiel</title><link rel="stylesheet" href="assets/style.css?v={asset_version}"><script type="module" src="assets/youtube-demo.mjs?v={asset_version}"></script><script type="module" src="assets/hints.mjs?v={asset_version}"></script><script type="module" src="assets/explorer.mjs?v={asset_version}"></script></head><body>
<a class="skip-link" href="#sources">Aller à la revue de presse</a><header id="top" tabindex="-1"><h1>Retrouver les références<br>de <em>La Riposte.</em></h1><p class="edition">Émission du 28 septembre 2026 · carnet de travail</p><p class="intro">Les sujets de l’émission, leurs passages et des articles associés. Un premier outil pour retrouver les références et les relire avec l’équipe.</p><p class="byline">Préparé par Thomas · <a href="mailto:thomas@codethelaw.eu">thomas@codethelaw.eu</a><br>Projet personnel non officiel, sans validation de Radio Nova ou de l’équipe.</p><p class="entry-actions"><a class="button" href="#sources">Explorer les sujets</a> <a class="secondary-link" href="https://www.youtube.com/watch?v=kKOcQM1eynE" target="_blank" rel="noopener noreferrer">Voir l’émission sur YouTube ↗</a></p></header>
<nav aria-label="Navigation principale"><a href="#proposal">Comprendre</a><a href="#sources">Explorer les sujets</a><a href="#excerpt">Essayer le lecteur</a><a href="#presentation">Présenter le projet</a></nav><main>
<section id="proposal"><h2>Un coup de main pour préparer et retrouver.</h2><p>J’aime La Riposte et j’ai préparé ce premier essai pour l’équipe : retrouver les sujets, relier des articles aux passages et disposer d’une base à relire.</p><ul><li>Une revue de presse à explorer et à corriger.</li><li>Une transcription et des sous-titres conservés en privé, à relire avec l’équipe.</li><li>Un court extrait pour essayer la lecture synchronisée.</li></ul><details class="editorial-note"><summary>Ce qui est partagé ici</summary><p>Cette page partage les synthèses et un court extrait de texte. La transcription complète et les sous-titres restent privés. Aucune vidéo, aucun audio ni article intégral n’est réhébergé : les liens ouvrent les publications d’origine.</p></details></section>
<section id="excerpt"><h2>Essayer le texte synchronisé</h2><p>Dix secondes de l’introduction, de 00:42 à 00:52. Activez le lecteur YouTube pour voir le texte suivre la vidéo.</p><details class="demo-privacy"><summary>Confidentialité du lecteur</summary><p id="demo-consent" class="compact">YouTube n’est contacté qu’après activation. Son lecteur et ses scripts transmettent notamment votre adresse IP et peuvent traiter d’autres données selon sa politique. Le mode youtube-nocookie.com limite certains usages des cookies, mais ne rend pas la lecture anonyme.</p></details><div class="demo-layout"><div class="demo-player"><div class="demo-video"><div id="demo-frame"><div id="demo-mount"></div></div><div id="demo-placeholder"><p>Le lecteur YouTube n’est pas chargé.</p><p class="compact">Activation volontaire · connexion Internet nécessaire</p></div></div><button id="demo-activate" class="action" type="button" aria-describedby="demo-consent" disabled>Activer YouTube et lire l’extrait</button><p id="demo-status" role="status" aria-live="polite">Activez YouTube pour essayer l’extrait.</p><p class="compact">Position : <span id="demo-time">—</span>. Si la lecture ne démarre pas, appuyez sur Lecture dans le lecteur YouTube.</p><p><a href="{esc(youtube(42))}" target="_blank" rel="noopener noreferrer">Voir cet extrait sur YouTube ↗</a></p></div><div class="demo-text"><div class="demo-controls"><button id="demo-reset" class="action" type="button" disabled>Relancer l’extrait</button><button id="demo-align" class="action" type="button" disabled>Reprendre le suivi</button><label><input id="demo-follow" type="checkbox" checked> Suivre la lecture</label></div><p id="demo-sync-status" class="compact" aria-live="polite">Suivi de la lecture activé.</p><div id="demo-transcript" tabindex="0" role="region" aria-label="Court extrait de transcription synchronisée">{''.join(excerpt)}</div><details class="editorial-note"><summary>Comment suivre le texte</summary><p>Cliquez sur une heure pour rejoindre la réplique. Avant activation, le lien ouvre YouTube ; une fois le lecteur prêt, il déplace la lecture ici. Faire défiler le texte suspend son suivi automatique. « Reprendre le suivi » le réactive. Seul ce court extrait est affiché.</p></details></div></div><noscript><p class="warning">Sans JavaScript, le texte et les liens restent accessibles. La lecture synchronisée n’est pas disponible.</p></noscript></section>
<section id="version"><h2>Une transcription à relire avec l’équipe</h2><p>Une version de travail couvre l’épisode d’environ 1 h 39 min, avec {french_number(metadata['segments'])} segments de sous-titres. Elle reste privée et n’a pas été intégralement vérifiée à l’écoute.</p><details class="editorial-note"><summary>Identifier la version du fichier</summary><p>Empreinte SHA-256 du fichier Markdown conservé en privé — {french_number(metadata['bytes'])} octets :</p><p class="fingerprint"><code>{metadata['sha256']}</code></p><p class="note">Cette empreinte sert à comparer les versions d’un fichier. Elle ne garantit ni l’exactitude ni la complétude de la transcription, et ne donne pas accès au fichier.</p><p><a href="data/version-transcription.json" download>Informations sur cette version (.json)</a></p></details></section>
<section id="sources"><h2>Les sujets, les passages, les sources.</h2><p class="hint-line">Une base à relire, pas un fact-checking de l’émission. <span class="hint-note">Un article associé peut éclairer un sujet sans confirmer tous les propos. Son statut de consultation est indiqué sous le lien.</span></p><p>{len(public)} sujets repérés : {counts['actualité']} sujets d’actualité, {counts['contexte']} références de contexte et {counts['anecdote / promotion']} anecdotes ou annonces.</p><details class="editorial-note"><summary>Comment lire les statuts et les sources</summary><p>Les synthèses reprennent les sujets évoqués dans l’émission, y compris des rappels anciens. Les articles associés ne sont pas nécessairement ceux utilisés par l’équipe.</p><p>« Article consulté » indique une lecture pendant la recherche, avec les éventuelles limites précisées dans la note. « Article repéré » signifie que son titre et ses informations de publication ont été trouvés, sans lecture du texte intégral. Les dates issues de ces résultats n’ont pas toutes été contrôlées sur le site de l’éditeur.</p><p>{associated} sujets ont au moins un article associé. Pour {read} sujets, au moins un article a été consulté ; cela ne signifie pas que ces sujets sont vérifiés.</p><p>La liste peut être incomplète. Les attributions incertaines et les correspondances partielles restent signalées.</p></details><p><a href="data/revue-de-presse.md" download>Télécharger la revue de presse (.md)</a> · <a href="data/sources.json" download>Télécharger les données des sources (.json)</a></p><div class="explorer-controls" hidden><label for="topic-search">Chercher un sujet, une personne ou un média</label><div class="search-row"><input id="topic-search" type="search" autocomplete="off" placeholder="Par exemple : retraites, Dati, franceinfo" aria-describedby="search-help"><button class="action" id="clear-search" type="button">Tout réafficher</button></div><p id="search-help" class="compact">Recherche sur cet appareil, sans envoi de vos mots-clés. Chaque mot est recherché au début d’un mot dans les titres, résumés, sources et notes.</p><div class="explorer-options"><fieldset><legend>Afficher</legend><label><input type="radio" name="category" value="all" checked> Tous les sujets</label><label><input type="radio" name="category" value="actualité"> Actualités</label><label><input type="radio" name="category" value="contexte"> Contexte</label><label><input type="radio" name="category" value="anecdote / promotion"> Anecdotes et annonces</label></fieldset><label class="order-label" for="topic-order">Ordre de lecture<select id="topic-order"><option value="category">Par catégorie</option><option value="time">Dans l’ordre de l’émission</option></select></label></div><p id="results-status" role="status" aria-atomic="true"></p><p id="no-results" hidden>Aucun sujet avec ces mots et ce filtre. Essayez un mot plus court ou réaffichez tous les sujets.</p></div><div class="category-links" role="navigation" aria-label="Familles de références"><a href="#actualites">Actualités</a><a href="#contextes">Références de contexte</a><a href="#anecdotes">Anecdotes et annonces</a></div><div id="topic-results">{''.join(parts)}<section class="topic-section" id="chronological" hidden><h2>Dans l’ordre de l’émission</h2><div id="chronological-list"></div></section></div><p id="share-status" role="status" aria-atomic="true"></p></section>
<section id="presentation"><h2>Un premier essai à tester avec l’équipe</h2><p>Un outil proposé par un auditeur pour retrouver les passages de La Riposte et les articles qui éclairent les sujets. Le repérage des sources et la transcription ont été réalisés avec l’aide de l’IA ; la relecture éditoriale reste nécessaire.</p><h3>À essayer maintenant</h3><ul><li>Rechercher un sujet et rejoindre son passage sur YouTube.</li><li>Lire les articles associés et identifier ce qui reste à vérifier.</li><li>Tester dix secondes de texte synchronisé.</li></ul><h3>Avant d’aller plus loin</h3><ul><li>Relire les synthèses, les correspondances et les sous-titres.</li><li>Choisir les usages utiles à l’équipe et les modalités de collaboration.</li><li>Définir les autorisations et les conditions d’une éventuelle publication.</li></ul><h3>Prochaine étape proposée</h3><p>Tester ensemble sur une émission, noter ce qui aide et ce qui gêne, puis décider de la suite. Les gains de temps et la fiabilité restent à évaluer.</p><p class="compact">Prototype personnel non officiel, sans validation de Radio Nova ou de l’équipe. La transcription complète reste privée.</p><p class="compact">Préparé par Thomas<span class="print-surname"> Suau</span> · <a href="mailto:thomas@codethelaw.eu">thomas@codethelaw.eu</a>.</p><p class="presentation-actions"><a href="#presentation">Lien vers cette présentation</a><button class="action" id="print-presentation" type="button" hidden>Imprimer la présentation</button></p><p class="compact print-help">L’impression de cette section peut aussi être enregistrée en PDF depuis le navigateur.</p></section>
<section id="contact"><h2>Un retour, une correction ?</h2><p>La transcription a été produite avec Whisper et des modèles d’IA, puis corrigée en partie à l’écoute. Elle peut encore contenir des erreurs.</p><p>Un sujet mal résumé, une source à ajouter ou une demande de retrait ? Écrivez-moi. Les droits sur les propos et les articles restent ceux de leurs ayants droit.</p><p><a href="mailto:thomas@codethelaw.eu">Écrire à Thomas ↗</a> · <a href="https://github.com/tsua0002/riposte-apercu" target="_blank" rel="noopener noreferrer">Voir le code ↗</a></p><details class="editorial-note"><summary>Confidentialité et fonctionnement du site</summary><p>Ce site ne comporte pas de formulaire ni d’outil de mesure d’audience. Le lecteur YouTube se charge uniquement après activation. Les liens vers les articles ouvrent les sites des éditeurs, soumis à leurs propres politiques. L’hébergeur peut conserver des journaux techniques.</p></details></section>
</main><footer><p class="compact">Projet personnel non officiel · <a href="mailto:thomas@codethelaw.eu">Contacter Thomas</a></p><a class="back-to-top" href="#top" hidden aria-label="Revenir en haut de la page"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m6 12 6-6 6 6M12 6v14"/></svg><span>En haut</span></a></footer></body></html>'''
(ROOT / 'data').mkdir(exist_ok=True)
hint_parser = NoteHints()
hint_parser.feed(page)
page = ''.join(hint_parser.output)
(ROOT / 'index.html').write_text(page)
(ROOT / 'data/sources.json').write_text(json.dumps(public, ensure_ascii=False, indent=2))
(ROOT / 'data/version-transcription.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
(ROOT / 'data/revue-de-presse.md').write_text('\n'.join(review))
print(f'Built public preview: {len(public)} topics, {len(excerpt)} short cues; no full transcript or media.')
