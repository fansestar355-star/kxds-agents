#!/usr/bin/env python3
# boss_issue_reply.py - Kélé répond aux commentaires Issues GitHub (HTTPS, meme PC eteint)
import os, json, urllib.request
from google import genai

repo = os.getenv('GITHUB_REPOSITORY', 'fansestar355-star/kxds-agents')
token = os.getenv('GITHUB_TOKEN')
key = os.getenv('GEMINI_API_KEY')

if not token or not key:
    print("Token ou GEMINI_KEY manquant")
    exit(0)

try:
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/issues?state=open&labels=kxds-boss', headers={'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'})
    issues = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    print(f"{len(issues)} Issues Boss")
    for iss in issues[:3]:
        cr = urllib.request.Request(iss['comments_url'], headers={'Authorization': f'token {token}'})
        comments = json.loads(urllib.request.urlopen(cr, timeout=10).read().decode())
        for c in comments[-2:]:
            body = c.get('body','')
            if 'Kélé' not in body and 'kélé' not in body.lower():
                print(f"Nouveau commentaire #{iss['number']} de {c['user']['login']}: {body[:100]}")
                try:
                    client = genai.Client(api_key=key)
                    prompt = f"Tu es Kélé - Griot Supreme. Reponds a ce commentaire GitHub sur l'Issue '{iss['title']}' : {body[:1000]}. 5 phrases max, ordonne une action aux agents si besoin."
                    reply = None
                    for m in ['gemini-3.5-flash','gemini-flash-latest']:
                        try:
                            r = client.models.generate_content(model=m, contents=prompt)
                            reply = r.text
                            break
                        except:
                            continue
                    if not reply:
                        reply = 'Merci pour ton retour, je transmets aux agents.'
                    data = json.dumps({'body': f"**Kélé répond:**\n{reply}"}).encode()
                    pr = urllib.request.Request(iss['comments_url'], data=data, headers={'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'})
                    urllib.request.urlopen(pr, timeout=10)
                    print(f"Reponse postee sur #{iss['number']}")
                except Exception as e:
                    print(f"Erreur reponse: {e}")
except Exception as e:
    print(f"Issues check echec: {e}")
