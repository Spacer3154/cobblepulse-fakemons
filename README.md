# CobblePulse Fakemons — mod « Normandy Fakemons »

Mod Fabric (Minecraft 1.21.1) de fakemons pour **Cobblemon 1.8.4**, avec **Mega Showdown** :
la région de **Normandie** (22 espèces) et la catégorie **Monster Hunter** (Deviljho, sa méga-évolution
Deviljho Carnage et la Deviljhonite).

- Contenu détaillé (espèces, modèles, animations, apparitions, talents, capacités, montures) : [docs/CONTENU.md](docs/CONTENU.md)
- Jar compilé par la CI : branche [`ci-output`](../../tree/ci-output) (`normandy_fakemons-<version>+mc1.21.1.jar`)

## Installation
Le jar va dans `mods/` du serveur **et** des clients. Dépendances : Fabric API, Cobblemon 1.8.4, Mega Showdown
(+ ses dépendances : Architectury API, Accessories, owo-lib). Biomes O' Plenty est conseillé (Deviljho apparaît
dans ses Wasteland).

## Organisation du dépôt
| Dossier | Rôle |
| --- | --- |
| `src/main/java/fr/cobblepulse/fakemons/` | Code : objets du mod (méga-gemmes), onglet créatif, auto-vérification au démarrage du serveur |
| `src/main/resources/` | Données et ressources : `data/cobblemon/…` (espèces, apparitions, Pokédex), `data/normandy/mega_showdown/…` (talents, capacités, objets Showdown, méga), `assets/cobblemon/bedrock/…` (modèles, animations, posers, resolvers), textures, langue |
| `tools/models/` | Générateur Python des modèles Bedrock, textures et animations (une espèce = `species/<id>.py`) |
| `tools/gen/` | Générateurs de données (apparitions, Monster Hunter) et validateur du pack |
| `tools/showdown/` | Tests Pokémon Showdown des capacités, talents et de la méga-évolution (Node) |
| `ci/` | Serveur de test de la CI |

## Compiler
```
./gradlew build          # -> build/libs/normandy_fakemons-<version>+mc1.21.1.jar
```
La CI (GitHub Actions, à chaque push sur `main`) : validateur du pack, tests Showdown, compilation, puis un vrai
serveur Fabric avec Cobblemon et Mega Showdown qui charge le mod (auto-test `-Dnormandy_fakemons.selftest=true`,
apparition de Deviljho et de sa forme Méga, Deviljhonite et ses composants). Résultats et jar : branche `ci-output`
(`CHECKS`, `server-summary.txt`, `server-errors.txt`, `server.log`).

## Régénérer un modèle
```
cd tools/models
bash iter.sh guillopard                                         # une espèce « classique »
python3 -I build_deviljho.py . ../../src/main/resources tmp     # Deviljho + Deviljho Carnage
python3 -I check_ground.py . guillopard                         # aucune partie sous le sol
python3 preview_anim.py guillopard tmp/apercu ground_walk:12    # GIF d'aperçu
cd ../.. && python3 tools/gen/monster_hunter.py                  # données Monster Hunter (Deviljho, Deviljhonite)
python3 tools/gen/validate_pack.py src/main/resources tools/showdown
```
Les fichiers Blockbench (`.bbmodel`) de chaque modèle sont rangés à part (poste de travail).

## Ajouter une méga-gemme
1. `src/main/java/.../NormandyFakemons.java` : `registerMegaStone("<nom>ite", ResourceLocation("normandy", "<nom>ite"), "<espece>")`.
2. `data/normandy/mega_showdown/mega/<nom>ite.json` et `data/normandy/mega_showdown/showdown/held_items/<nom>ite.js`.
3. Forme `Mega` dans l'espèce, assignation de la feature `mega_evolution`, resolver/poser/modèle de la forme.
4. Modèle d'objet `assets/normandy_fakemons/models/item/<nom>ite.json`, icône et textes (`item.normandy_fakemons.<nom>ite`, `.lore`, `.lore2`).
