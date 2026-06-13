import urllib.request
import csv
import bs4
import re
import pandas as pd
import folium
import webbrowser
import json

# ----------------------------
# UTILITAIRE D’HARMONISATION
# ----------------------------
def normaliser_nom_ville(ville):
    """Nettoie et harmonise les noms de ville pour correspondance fiable."""
    if not isinstance(ville, str) or not ville.strip():
        return ""
    # Supprime les crochets et leur contenu
    ville = re.sub(r"\[.*?\]", "", ville)
    ville = ville.strip().lower()

    # Remplace les apostrophes typographiques et espaces multiples
    ville = ville.replace("’", "'")
    ville = re.sub(r"\s+", " ", ville)

    # Met la première lettre de chaque mot en majuscule
    ville = ville.title()

    # Corrige les abréviations courantes
    ville = re.sub(r"\bSt\b", "Saint", ville)
    ville = re.sub(r"\bSte\b", "Sainte", ville)
    ville = re.sub(r"\bSte-\b", "Sainte-", ville)
    ville = re.sub(r"\bSt-\b", "Saint-", ville)

    return ville

# ----------------------------
# FONCTIONS DE SCRAPING
# ----------------------------
def get_total_offres(url):
    page = urllib.request.urlopen(url).read()
    soup = bs4.BeautifulSoup(page.decode('utf-8'), "html.parser")
    texte_total = soup.find('h1', {'class': 'title'}).get_text(strip=True)
    return int(re.search(r"\d+", texte_total).group())

def scrape_offres(base_url, total_offres, step=20):
    codes, villes, contrats = [], [], []

    for start in range(0, total_offres, step):
        end = start + step - 1
        url = base_url if start == 0 else (
            f"https://candidat.francetravail.fr/offres/recherche.rechercheoffre:afficherplusderesultats/"
            f"{start}-{end}/0?lieux=75R&motsCles=data&offresPartenaires=true&rayon=10&tri=0"
        )
        page = urllib.request.urlopen(url).read()
        soup = bs4.BeautifulSoup(page.decode('utf-8'), "html.parser")

        contrats_html = soup.find_all('p', {'class': 'contrat'})
        lieux_html = soup.find_all('p', {'class': 'subtext'})

        for c in contrats_html:
            contrats.append(c.contents[0].strip().split()[0] if c.contents else "")

        for l in lieux_html:
            span = l.find('span')
            if span:
                parts = span.get_text(strip=True).split('-')
                code = parts[0].strip()
                ville = '-'.join(parts[1:]).strip()
                ville = normaliser_nom_ville(ville)
                villes.append(ville)
                codes.append(code)

    return codes, villes, contrats

def save_csv(filename, codes, villes, contrats):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Code", "Ville", "Contrat"])
        writer.writerows(zip(codes, villes, contrats))

def get_coordinates(base_url, villes_liste):
    page = urllib.request.urlopen(base_url).read()
    soup = bs4.BeautifulSoup(page, "lxml")

    tab_villes = soup.find('table', {'class': 'table table-hover small'})
    if not tab_villes:
        return {}

    lignes = tab_villes.find_all('tr')
    df = pd.DataFrame(columns=['Ville', 'Insee', 'Latitude', 'Longitude'])

    for ligne in lignes:
        cellules = ligne.find_all('td')
        if len(cellules) < 9:
            continue

        ville = cellules[0].get_text(strip=True)
        ville = normaliser_nom_ville(ville)
        insee = cellules[1].get_text(strip=True)
        lat = cellules[7].get_text(strip=True)
        lon = cellules[8].get_text(strip=True)

        try:
            lat = float(lat.replace(',', '.'))
            lon = float(lon.replace(',', '.'))
        except ValueError:
            continue

        df.loc[len(df)] = [ville, insee, lat, lon]

    # Garde uniquement les villes présentes dans la liste des offres
    df_filtre = df[df['Ville'].isin(villes_liste)]

    coord_dict = {
        row['Ville']: {'Latitude': row['Latitude'], 'Longitude': row['Longitude']}
        for _, row in df_filtre.iterrows()
    }

    return coord_dict

def create_map(df, output_html="map.html"):
    carte = folium.Map(location=[46.5, 0], zoom_start=6)

    for _, row in df.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        if pd.notnull(lat) and pd.notnull(lon):
            popup_text = f"<b>{row['Ville']}</b><br>Contrats: {row['Contrat']}"
            folium.Marker([lat, lon], popup=folium.Popup(popup_text, max_width=300)).add_to(carte)

    with open("regions-5m.geojson", encoding="utf-8") as f:
        geojson_data = json.load(f)

    na_geo = {
        "type": "FeatureCollection",
        "features": [
            feature for feature in geojson_data["features"]
            if feature["properties"].get("nom") == "Nouvelle-Aquitaine"
        ]
    }

    folium.GeoJson(
        na_geo,
        name="Nouvelle-Aquitaine",
        style_function=lambda x: {'color': 'red', 'weight': 3, 'fill': False, 'dashArray': '5, 5'}
    ).add_to(carte)

    carte.save(output_html)
    webbrowser.open_new_tab(output_html)

# ----------------------------
# SCRIPT PRINCIPAL
# ----------------------------
base_url_offres = "https://candidat.francetravail.fr/offres/recherche?lieux=75R&motsCles=data&offresPartenaires=true&rayon=10&tri=0"
base_url_villes = "https://france.comersis.com/listes-des-villes-de-Nouvelle-Aquitaine-201.html"

total_offres = get_total_offres(base_url_offres)
codes, villes, contrats = scrape_offres(base_url_offres, total_offres)
save_csv("Emplois.csv", codes, villes, contrats)

df_emplois = pd.read_csv("Emplois.csv", sep=';')
df_emplois['Ville'] = df_emplois['Ville'].apply(normaliser_nom_ville)

df_villes_unique = df_emplois[['Code', 'Ville']].drop_duplicates()

coord_dict = get_coordinates(base_url_villes, df_villes_unique['Ville'].tolist())
df_villes_unique['Latitude'] = df_villes_unique['Ville'].map(lambda x: coord_dict.get(x, {}).get('Latitude'))
df_villes_unique['Longitude'] = df_villes_unique['Ville'].map(lambda x: coord_dict.get(x, {}).get('Longitude'))

df_emplois = df_emplois.merge(
    df_villes_unique[['Code', 'Ville', 'Latitude', 'Longitude']],
    on=['Code', 'Ville'],
    how='left'
)

df_contrats_group = df_emplois.groupby(['Code', 'Ville']).agg({
    'Contrat': lambda x: ', '.join(f"{c} ({sum(x==c)})" for c in sorted(set(x)))
}).reset_index()

df_contrats_group = df_contrats_group.merge(
    df_villes_unique[['Code', 'Ville', 'Latitude', 'Longitude']],
    on=['Code', 'Ville'],
    how='left'
)

create_map(df_contrats_group, "Map.html")
df_contrats_group.to_csv("Emplois_geo.csv", sep=';', index=False)
