# CobblePulse-Ecology (anciennement « Normandy Fakemons »)

Mod Fabric (Minecraft 1.21.1) de fakemons pour **Cobblemon 1.8.4**, avec **Mega Showdown** :
la région de **Normandie** (22 espèces) et la catégorie **Monster Hunter** : Deviljho (méga : Deviljho Carnage,
Deviljhonite) et Glavenus (méga : Glavenus Lame-Chaos, Glavenusite).

- Contenu détaillé (espèces, modèles, animations, apparitions, talents, capacités, montures) : [docs/CONTENU.md](docs/CONTENU.md)
- Jar compilé par la CI : branche [`ci-output`](../../tree/ci-output) (`cobblepulse-ecology-<version>+mc1.21.1.jar`)

## Installation
Le jar va dans `mods/` du serveur **et** des clients (il remplace l'ancien `normandy_fakemons-*.jar`, à retirer).
Dépendances : Fabric API, Cobblemon 1.8.4, Mega Showdown (+ ses dépendances : Architectury API, Accessories,
owo-lib). Biomes O' Plenty est conseillé (Deviljho apparaît dans ses Wasteland).

Identifiants : mod `cobblepulse_ecology`, objets `cobblepulse_ecology:deviljhonite` et `cobblepulse_ecology:glavenusite`.
Les données gardent l'espace de noms `normandy` (`normandy:deviljhonite`, `/function normandy:give_glavenusite`…).
L'ancien identifiant `normandy_fakemons:deviljhonite` (mod 2.3) reste enregistré : les Deviljhonites déjà fabriquées
restent valables.

## Organisation du dépôt
| Dossier | Rôle |
| --- | --- |
| `src/main/java/fr/cobblepulse/ecology/` | Code : objets du mod (méga-gemmes), onglet créatif, auto-vérification au démarrage du serveur |
| `src/main/resources/` | Données et ressources : `data/cobblemon/…` (espèces, apparitions, Pokédex), `data/normandy/mega_showdown/…` (talents, capacités, objets Showdown, méga), `assets/cobblemon/bedrock/…` (modèles, animations, posers, resolvers), textures, langue |
| `tools/models/` | Générateur Python des modèles Bedrock, textures et animations (une espèce = `species/<id>.py`) |
| `tools/gen/` | Générateurs de données (apparitions, Monster Hunter) et validateur du pack |
| `tools/showdown/` | Tests Pokémon Showdown des capacités, talents et des méga-évolutions (Node) |
| `ci/` | Serveur de test de la CI |

## Compiler
```
./gradlew build          # -> build/libs/cobblepulse-ecology-<version>+mc1.21.1.jar
```
La CI (GitHub Actions, à chaque push sur `main`) : validateur du pack, tests Showdown, compilation, puis un vrai
serveur Fabric avec Cobblemon et Mega Showdown qui charge le mod (auto-test `-Dcobblepulse_ecology.selftest=true`,
apparition de Deviljho, de Glavenus et de leurs formes Méga, méga-gemmes et leurs composants, recettes). Résultats et
jar : branche `ci-output` (`CHECKS`, `server-summary.txt`, `server-errors.txt`, `server.log`).

## Régénérer un modèle
```
cd tools/models
bash iter.sh guillopard                                              # une espèce « classique »
python3 -I build_mh.py . deviljho ../../src/main/resources tmp       # Monster Hunter : espèce + forme Méga
python3 -I build_mh.py . glavenus ../../src/main/resources tmp       # (écrit aussi tmp/<espèce>_tops.json)
cp tmp/glavenus_tops.json ../gen/                                    # hauteurs du modèle -> baseScale
python3 -I check_ground.py . guillopard                              # aucune partie sous le sol
python3 preview_anim.py guillopard tmp/apercu ground_walk:12         # GIF d'aperçu
cd ../.. && python3 tools/gen/monster_hunter.py                       # données Monster Hunter (espèces, méga-gemmes)
python3 tools/gen/validate_pack.py src/main/resources tools/showdown
```
Les fichiers Blockbench (`.bbmodel`) de chaque modèle sont rangés à part (poste de travail).

## Ajouter une méga-gemme
1. `CobblePulseEcology.java` : `registerMegaStone(id("<nom>ite"), data("<nom>ite"), "<espece>", MEGA_STONES)`.
2. `tools/gen/monster_hunter.py` : `mega_stone("<nom>ite", "<Espece>", num=…, recipe=…, lore=…, lore2=…)` écrit
   l'entrée `mega_showdown/mega`, l'objet Showdown, la recette `normandy:<nom>ite`, la fonction `give`, le modèle
   d'objet `assets/cobblepulse_ecology/models/item/<nom>ite.json` et les textes (icône : `tools/gen/<nom>ite.png`).
3. Forme `Mega` dans l'espèce, assignation de la feature `mega_evolution`, resolver/poser/modèle de la forme.
