package fr.cobblepulse.ecology;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.item.v1.DefaultItemComponentEvents;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * CobblePulse-Ecology (anciennement Normandy Fakemons) : le contenu (especes, modeles, apparitions, Showdown...) est
 * dans les ressources du jar ; le code enregistre les vrais objets du mod, a commencer par les mega-gemmes
 * (Deviljhonite, Glavenusite), la forme Armure de Glace de Zamtrios dans les biomes geles (ZamtriosClimate) et les
 * starters de Normandie dans le choix du starter (NormandyStarters).
 *
 * Une mega-gemme est reconnue par Mega Showdown grace a deux composants de donnees poses par defaut sur l'objet :
 * mega_showdown:registry_type_component = "mega" et mega_showdown:registry_location_component = l'entree du registre
 * datapack mega_showdown:mega (ex. normandy:deviljhonite). On les recupere par leur identifiant, sans dependance de
 * compilation a Mega Showdown.
 */
public final class CobblePulseEcology implements ModInitializer {
    public static final String MOD_ID = "cobblepulse_ecology";
    public static final Logger LOG = LoggerFactory.getLogger("CobblePulseEcology");
    /** Espace de noms des donnees (especes, registre mega, recettes...) : inchange depuis Normandy Fakemons. */
    public static final String DATA_NS = "normandy";

    /** Mega-gemmes du mod : objet -> (entree du registre mega de Mega Showdown, espece concernee). */
    public static final List<MegaStoneItem> MEGA_STONES = new ArrayList<>();
    /** Anciens identifiants (mod 2.3, normandy_fakemons:...) : toujours valides, hors onglets creatifs. */
    public static final List<MegaStoneItem> LEGACY_STONES = new ArrayList<>();

    public static Item DEVILJHONITE;
    public static Item GLAVENUSITE;
    public static final ResourceKey<CreativeModeTab> TAB = ResourceKey.create(Registries.CREATIVE_MODE_TAB, id("fakemons"));
    private static final ResourceKey<CreativeModeTab> MSD_MEGA_TAB =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, ResourceLocation.fromNamespaceAndPath("mega_showdown", "mega_tab"));
    private static final ResourceLocation MSD_TYPE = ResourceLocation.fromNamespaceAndPath("mega_showdown", "registry_type_component");
    private static final ResourceLocation MSD_LOCATION = ResourceLocation.fromNamespaceAndPath("mega_showdown", "registry_location_component");

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }

    private static ResourceLocation data(String path) {
        return ResourceLocation.fromNamespaceAndPath(DATA_NS, path);
    }

    @Override
    public void onInitialize() {
        DEVILJHONITE = registerMegaStone(id("deviljhonite"), data("deviljhonite"), "deviljho", MEGA_STONES);
        GLAVENUSITE = registerMegaStone(id("glavenusite"), data("glavenusite"), "glavenus", MEGA_STONES);
        // Deviljhonites fabriquees avec le mod 2.3 (normandy_fakemons:deviljhonite) : elles restent utilisables
        registerMegaStone(ResourceLocation.fromNamespaceAndPath("normandy_fakemons", "deviljhonite"), data("deviljhonite"),
                "deviljho", LEGACY_STONES);

        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, TAB, FabricItemGroup.builder()
                .title(Component.translatable("itemGroup.cobblepulse_ecology.fakemons"))
                .icon(() -> new ItemStack(GLAVENUSITE))
                .displayItems((params, output) -> MEGA_STONES.forEach(output::accept))
                .build());
        // aussi dans l'onglet des mega-gemmes de Mega Showdown (si present)
        ItemGroupEvents.modifyEntriesEvent(MSD_MEGA_TAB).register(entries -> MEGA_STONES.forEach(entries::accept));

        // composants Mega Showdown poses par defaut sur chaque mega-gemme (apres l'init de tous les mods)
        DefaultItemComponentEvents.MODIFY.register(context -> {
            DataComponentType<String> type = component(MSD_TYPE);
            DataComponentType<ResourceLocation> location = component(MSD_LOCATION);
            if (type == null || location == null) {
                LOG.error("Mega Showdown introuvable : les mega-gemmes de CobblePulse-Ecology ne permettront pas de mega-evoluer");
                return;
            }
            for (MegaStoneItem stone : allStones()) {
                context.modify(stone, builder -> {
                    builder.set(type, "mega");
                    builder.set(location, stone.megaEntry());
                });
            }
        });

        ZamtriosClimate.register();
        NormandyStarters.register();                       // avant selfCheck : meme evenement, enregistre en premier
        ServerLifecycleEvents.SERVER_STARTED.register(CobblePulseEcology::selfCheck);
        LOG.info("CobblePulse-Ecology : {} mega-gemme(s) enregistree(s)", MEGA_STONES.size());
    }

    private static List<MegaStoneItem> allStones() {
        List<MegaStoneItem> all = new ArrayList<>(MEGA_STONES);
        all.addAll(LEGACY_STONES);
        return all;
    }

    private static MegaStoneItem registerMegaStone(ResourceLocation itemId, ResourceLocation megaEntry, String species,
                                                   List<MegaStoneItem> list) {
        MegaStoneItem item = Registry.register(BuiltInRegistries.ITEM, itemId,
                new MegaStoneItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), megaEntry, species));
        list.add(item);
        return item;
    }

    @SuppressWarnings("unchecked")
    private static <T> DataComponentType<T> component(ResourceLocation key) {
        return (DataComponentType<T>) BuiltInRegistries.DATA_COMPONENT_TYPE.get(key);
    }

    /** Verification au demarrage du serveur : un resume dans les logs (detaille avec -Dcobblepulse_ecology.selftest=true). */
    private static void selfCheck(MinecraftServer server) {
        boolean verbose = Boolean.getBoolean("cobblepulse_ecology.selftest");
        List<String> problems = new ArrayList<>();
        DataComponentType<String> type = component(MSD_TYPE);
        DataComponentType<ResourceLocation> location = component(MSD_LOCATION);
        ResourceKey<Registry<Object>> megaKey = ResourceKey.createRegistryKey(ResourceLocation.fromNamespaceAndPath("mega_showdown", "mega"));
        Optional<Registry<Object>> megaRegistry = server.registryAccess().registry(megaKey);
        for (MegaStoneItem stone : allStones()) {
            ItemStack stack = new ItemStack(stone);
            boolean ok = type != null && location != null && "mega".equals(stack.get(type)) && stone.megaEntry().equals(stack.get(location));
            if (!ok) problems.add(BuiltInRegistries.ITEM.getKey(stone) + " : composants Mega Showdown absents");
            if (megaRegistry.isEmpty() || !megaRegistry.get().containsKey(stone.megaEntry()))
                problems.add(stone.megaEntry() + " absent du registre mega_showdown:mega");
            if (verbose) LOG.info("SELFTEST item {} components={} mega_entry_loaded={}", BuiltInRegistries.ITEM.getKey(stone), ok,
                    megaRegistry.map(r -> r.containsKey(stone.megaEntry())).orElse(false));
        }
        int recipes = 0;
        for (MegaStoneItem stone : MEGA_STONES) {
            ResourceLocation r = data(BuiltInRegistries.ITEM.getKey(stone).getPath());
            boolean loaded = server.getRecipeManager().byKey(r).isPresent();
            if (loaded) recipes++;
            else problems.add("recette " + r + " non chargee");
            if (verbose) LOG.info("SELFTEST recipe {} loaded={}", r, loaded);
        }
        // formes de combat (Zamtrios Armure / Gonfle, Gore Magala Mode Furie) : registre battle_form de Mega Showdown
        ResourceKey<Registry<Object>> formKey = ResourceKey.createRegistryKey(ResourceLocation.fromNamespaceAndPath("mega_showdown", "battle_form"));
        Optional<Registry<Object>> formRegistry = server.registryAccess().registry(formKey);
        for (String f : BATTLE_FORMS) {
            boolean loaded = formRegistry.isPresent() && formRegistry.get().containsKey(data(f));
            if (!loaded) problems.add(data(f) + " absent du registre mega_showdown:battle_form");
            if (verbose) LOG.info("SELFTEST battle_form {} loaded={}", data(f), loaded);
        }
        int species = 0;
        for (String sid : SPECIES) {
            Object sp = cobblemonSpecies(sid);
            if (sp == null) problems.add("espece " + sid + " non chargee");
            else species++;
            if (verbose) LOG.info("SELFTEST species {} loaded={}", sid, sp != null);
        }
        // starters de Normandie dans le choix du starter (NormandyStarters)
        List<String> starterTabs = new ArrayList<>();
        String starterProblem = NormandyStarters.check(starterTabs);
        if (starterProblem != null) problems.add(starterProblem);
        if (verbose) LOG.info("SELFTEST starters {} tabs={}", starterProblem == null ? "ok" : starterProblem, starterTabs);
        if (problems.isEmpty()) {
            LOG.info("CobblePulse-Ecology OK : {}/{} especes, {} mega-gemme(s), {} recette(s) chargee(s), starters de Normandie",
                    species, SPECIES.length, MEGA_STONES.size(), recipes);
        } else {
            for (String p : problems) LOG.error("CobblePulse-Ecology : {}", p);
        }
        if (verbose) LOG.info("SELFTEST SUMMARY cobblepulse_ecology {} ({} probleme(s))", problems.isEmpty() ? "PASS" : "FAIL", problems.size());
    }

    static final String[] SPECIES = {"pomdraco", "arboverger", "cidrac", "drakflam", "vikinav", "drakkarthor", "meuhgousse",
            "bovecume", "normanguer", "etreroch", "archeolithe", "gargoylbatre", "rousselin", "roussinage", "homarbleu",
            "noroimard", "bolvados", "cruchevados", "alchibec", "archangelis", "sleipcheron", "guillopard", "deviljho",
            "glavenus", "zamtrios", "goremagala", "chaoticgoremagala", "shagarumagala"};
    static final String[] BATTLE_FORMS = {"zamtrios_armor", "zamtrios_inflated", "goremagala_frenzy"};

    /** PokemonSpecies.INSTANCE.getByName(name) de Cobblemon, par reflexion (pas de dependance de compilation). */
    private static Object cobblemonSpecies(String name) {
        try {
            Class<?> c = Class.forName("com.cobblemon.mod.common.api.pokemon.PokemonSpecies");
            Object instance = c.getField("INSTANCE").get(null);
            Method m = c.getMethod("getByName", String.class);
            return m.invoke(instance, name);
        } catch (Throwable t) {
            return null;
        }
    }
}
