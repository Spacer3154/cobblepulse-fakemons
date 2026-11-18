package fr.cobblepulse.ecology;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.Set;

/**
 * Zamtrios dans le monde : forme Armure de Glace dans les biomes geles (la ou il neige a sa hauteur), forme normale
 * ailleurs. Toutes les 2 secondes, pour chaque Zamtrios present dans le monde (sauvage ou sorti par un dresseur) et
 * hors combat, la caracteristique d'espece "zamtrios_form" est mise a "armor" ou "normal". En combat, ce sont
 * Showdown (condition d'espece) et Mega Showdown (registre battle_form) qui changent la forme ; ils la remettent a
 * "normal" a la fin du combat et ce tic la corrige ensuite selon le biome (une forme Gonflee restee apres un arret du
 * serveur en plein combat est corrigee de la meme facon).
 *
 * Cobblemon est appele par reflexion (pas de dependance de compilation) : PokemonEntity.getPokemon / isBattling,
 * Pokemon.getSpecies().getName() / getAspects(), new StringSpeciesFeature(nom, valeur).apply(pokemon).
 */
final class ZamtriosClimate {
    private static final int PERIOD = 40;
    private static Class<?> entityClass;
    private static Method getPokemon, isBattling, getSpecies, getName, getAspects, apply;
    private static Constructor<?> feature;
    private static boolean ready, broken, warned;
    private static final boolean VERBOSE = Boolean.getBoolean("cobblepulse_ecology.selftest");

    private ZamtriosClimate() {
    }

    static void register() {
        ServerTickEvents.END_WORLD_TICK.register(level -> {
            if (level.getGameTime() % PERIOD == 0) tick(level);
        });
    }

    private static boolean init() {
        if (ready) return true;
        if (broken) return false;
        try {
            entityClass = Class.forName("com.cobblemon.mod.common.entity.pokemon.PokemonEntity");
            Class<?> pokemon = Class.forName("com.cobblemon.mod.common.pokemon.Pokemon");
            Class<?> species = Class.forName("com.cobblemon.mod.common.pokemon.Species");
            Class<?> stringFeature = Class.forName("com.cobblemon.mod.common.api.pokemon.feature.StringSpeciesFeature");
            getPokemon = entityClass.getMethod("getPokemon");
            isBattling = entityClass.getMethod("isBattling");
            getSpecies = pokemon.getMethod("getSpecies");
            getName = species.getMethod("getName");
            getAspects = pokemon.getMethod("getAspects");
            feature = stringFeature.getConstructor(String.class, String.class);
            apply = stringFeature.getMethod("apply", pokemon);
            ready = true;
        } catch (Throwable t) {
            broken = true;
            CobblePulseEcology.LOG.warn("Zamtrios : formes du monde desactivees (Cobblemon introuvable ou API changee : {})", t.toString());
        }
        return ready;
    }

    /** Biome gele a cette position : assez froid pour qu'il y neige (banquise, pics de glace, montagnes enneigees...). */
    static boolean frozen(ServerLevel level, BlockPos pos) {
        return level.getBiome(pos).value().coldEnoughToSnow(pos);
    }

    private static void tick(ServerLevel level) {
        if (!init()) return;
        for (Entity e : level.getAllEntities()) {
            if (!entityClass.isInstance(e) || e.isRemoved()) continue;
            try {
                if ((Boolean) isBattling.invoke(e)) continue;
                Object pokemon = getPokemon.invoke(e);
                if (!"Zamtrios".equals(getName.invoke(getSpecies.invoke(pokemon)))) continue;
                @SuppressWarnings("unchecked")
                Set<String> aspects = (Set<String>) getAspects.invoke(pokemon);
                String have = aspects.contains("zamtrios-armor") ? "armor" : aspects.contains("zamtrios-inflated") ? "inflated" : "normal";
                String want = frozen(level, e.blockPosition()) ? "armor" : "normal";
                if (!want.equals(have)) {
                    apply.invoke(feature.newInstance("zamtrios_form", want), pokemon);
                    if (VERBOSE) CobblePulseEcology.LOG.info("SELFTEST zamtrios_form {} -> {} at {} (now {})", have, want,
                            e.blockPosition().toShortString(), getAspects.invoke(pokemon));
                }
            } catch (Throwable t) {
                if (!warned) {
                    warned = true;
                    CobblePulseEcology.LOG.warn("Zamtrios : changement de forme impossible ({})", t.toString());
                }
            }
        }
    }
}
