package fr.cobblepulse.ecology;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * Starters de Normandie (Kevin, 3.10.2) : Pomdraco (Plante), Drakflam (Feu) et Meuhgousse (Eau) proposes au choix du
 * starter de debut d'aventure, dans un onglet « Normandie » place avant les regions officielles (qui restent toutes).
 *
 * Cobblemon 1.8.4 : le gestionnaire de starters (CobblemonStarterHandler.getStarterList) renvoie les categories des
 * datapacks (StarterDataLoader) s'il y en a, sinon la liste de la config (Cobblemon.starterConfig.starters : les
 * regions officielles codees en dur, ou config/cobblemon/starters.json si exportStarterConfig est actif). On ajoute
 * la categorie Normandie a cette liste au demarrage du serveur et apres chaque /reload, sans toucher au fichier de
 * config, et sans doublon si l'entree a deja ete ajoutee a la main dans starters.json. Tout passe par reflexion
 * (pas de dependance de compilation a Cobblemon).
 */
final class NormandyStarters {
    static final String NAME = "Normandie";
    static final String DISPLAY_KEY = "cobblemon.starterselection.category.normandie";
    /** les regions officielles vont de -110 (Kanto) a -100 (Special) ; l'ordre croissant les range : Normandie en tete */
    static final int ORDER = -120;
    static final String[] POKEMON = {"pomdraco level=10", "drakflam level=10", "meuhgousse level=10"};
    static final String[] SPECIES = {"pomdraco", "drakflam", "meuhgousse"};

    private NormandyStarters() {
    }

    static void register() {
        ServerLifecycleEvents.SERVER_STARTED.register(server -> inject());
        ServerLifecycleEvents.END_DATA_PACK_RELOAD.register((server, resources, success) -> inject());
    }

    /** Ajoute la categorie a la liste de la config si elle n'y est pas ; renvoie un compte rendu pour les logs. */
    static synchronized String inject() {
        try {
            Object config = starterConfig();
            List<Object> starters = categories(config);
            if (findOurs(starters) != null) return "deja presente";
            Object ours = newCategory();
            try {
                starters.add(ours);
            } catch (UnsupportedOperationException e) {         // liste immuable : on la remplace par une copie
                List<Object> copy = new ArrayList<>(starters);
                copy.add(ours);
                config.getClass().getMethod("setStarters", List.class).invoke(config, copy);
            }
            CobblePulseEcology.LOG.info("CobblePulse-Ecology : starters de Normandie ajoutes ({})", String.join(", ", SPECIES));
            return "ajoutee";
        } catch (Throwable t) {
            CobblePulseEcology.LOG.error("CobblePulse-Ecology : impossible d'ajouter les starters de Normandie", t);
            return "erreur " + t;
        }
    }

    /**
     * Verification (auto-test) : la liste effective du choix du starter contient-elle l'onglet Normandie avec les 3 ?
     * Renvoie null si oui, sinon le probleme. detail recoit la liste des onglets effectifs.
     */
    static String check(List<String> detail) {
        try {
            List<Object> effective = new ArrayList<>(datapackCategories());
            String source = "datapacks";
            if (effective.isEmpty()) {
                effective = categories(starterConfig());
                source = "config";
            }
            for (Object c : effective) {
                detail.add(call(c, "getName") + "(" + call(c, "getOrder") + ")");
            }
            detail.add("source=" + source);
            Object ours = findOurs(effective);
            if (ours == null) {
                return "starters de Normandie absents du choix du starter (source " + source + ")";
            }
            List<String> got = new ArrayList<>();
            for (Object p : (Collection<?>) call(ours, "getPokemon")) got.add(String.valueOf(call(p, "getSpecies")));
            for (String s : SPECIES) {
                if (!got.contains(s)) return "starter " + s + " absent de l'onglet Normandie (" + got + ")";
                if (cobblemonSpecies(s) == null) return "espece de starter " + s + " non chargee";
            }
            return null;
        } catch (Throwable t) {
            return "verification des starters impossible : " + t;
        }
    }

    // ---------------------------------------------------------------------------------------- reflexion Cobblemon
    private static Object starterConfig() throws Exception {
        Class<?> cobblemon = Class.forName("com.cobblemon.mod.common.Cobblemon");
        Object instance = cobblemon.getField("INSTANCE").get(null);
        return cobblemon.getMethod("getStarterConfig").invoke(instance);
    }

    @SuppressWarnings("unchecked")
    private static List<Object> categories(Object config) throws Exception {
        return (List<Object>) config.getClass().getMethod("getStarters").invoke(config);
    }

    private static Collection<?> datapackCategories() {
        try {
            Class<?> loader = Class.forName("com.cobblemon.mod.common.data.StarterDataLoader");
            Object instance = loader.getField("INSTANCE").get(null);
            return (Collection<?>) loader.getMethod("getAllCategories").invoke(instance);
        } catch (Throwable t) {
            return List.of();
        }
    }

    /** l'onglet Normandie (par son nom) ou tout onglet qui propose deja Pomdraco (entree ajoutee a la main) */
    private static Object findOurs(Collection<?> categories) throws Exception {
        for (Object c : categories) {
            if (NAME.equalsIgnoreCase(String.valueOf(call(c, "getName")))) return c;
            for (Object p : (Collection<?>) call(c, "getPokemon")) {
                if (SPECIES[0].equalsIgnoreCase(String.valueOf(call(p, "getSpecies")))) return c;
            }
        }
        return null;
    }

    private static Object newCategory() throws Exception {
        Class<?> category = Class.forName("com.cobblemon.mod.common.config.starter.StarterCategory");
        Constructor<?> ctor = category.getConstructor(String.class, int.class, String.class, List.class, boolean.class);
        List<Object> pokemon = new ArrayList<>();
        for (String p : POKEMON) pokemon.add(parseProperties(p));
        return ctor.newInstance(NAME, ORDER, DISPLAY_KEY, pokemon, false);
    }

    /** PokemonProperties.Companion.parse(texte, " ", "=") */
    private static Object parseProperties(String text) throws Exception {
        Class<?> props = Class.forName("com.cobblemon.mod.common.api.pokemon.PokemonProperties");
        Object companion = props.getField("Companion").get(null);
        Method parse = companion.getClass().getMethod("parse", String.class, String.class, String.class);
        return parse.invoke(companion, text, " ", "=");
    }

    private static Object call(Object target, String method) throws Exception {
        return target.getClass().getMethod(method).invoke(target);
    }

    private static Object cobblemonSpecies(String name) {
        try {
            Class<?> c = Class.forName("com.cobblemon.mod.common.api.pokemon.PokemonSpecies");
            Object instance = c.getField("INSTANCE").get(null);
            return c.getMethod("getByName", String.class).invoke(instance, name);
        } catch (Throwable t) {
            return null;
        }
    }
}
