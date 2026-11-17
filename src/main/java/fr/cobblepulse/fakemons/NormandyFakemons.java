package fr.cobblepulse.fakemons;

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
 * Normandy Fakemons : le contenu (especes, modeles, apparitions, Showdown...) est dans les ressources du jar ;
 * le code enregistre les vrais objets du mod, a commencer par les mega-gemmes (Deviljhonite).
 *
 * Une mega-gemme est reconnue par Mega Showdown grace a deux composants de donnees poses par defaut sur l'objet :
 * mega_showdown:registry_type_component = "mega" et mega_showdown:registry_location_component = l'entree du registre
 * datapack mega_showdown:mega (ici normandy:deviljhonite). On les recupere par leur identifiant, sans dependance de
 * compilation a Mega Showdown.
 */
public final class NormandyFakemons implements ModInitializer {
    public static final String MOD_ID = "normandy_fakemons";
    public static final Logger LOG = LoggerFactory.getLogger("NormandyFakemons");

    /** Mega-gemmes du mod : objet -> (entree du registre mega de Mega Showdown, espece concernee). */
    public static final List<MegaStoneItem> MEGA_STONES = new ArrayList<>();

    public static Item DEVILJHONITE;
    public static final ResourceKey<CreativeModeTab> TAB = ResourceKey.create(Registries.CREATIVE_MODE_TAB, id("fakemons"));
    private static final ResourceKey<CreativeModeTab> MSD_MEGA_TAB =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, ResourceLocation.fromNamespaceAndPath("mega_showdown", "mega_tab"));
    private static final ResourceLocation MSD_TYPE = ResourceLocation.fromNamespaceAndPath("mega_showdown", "registry_type_component");
    private static final ResourceLocation MSD_LOCATION = ResourceLocation.fromNamespaceAndPath("mega_showdown", "registry_location_component");

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }

    @Override
    public void onInitialize() {
        DEVILJHONITE = registerMegaStone("deviljhonite", ResourceLocation.fromNamespaceAndPath("normandy", "deviljhonite"), "deviljho");

        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, TAB, FabricItemGroup.builder()
                .title(Component.translatable("itemGroup.normandy_fakemons.fakemons"))
                .icon(() -> new ItemStack(DEVILJHONITE))
                .displayItems((params, output) -> MEGA_STONES.forEach(output::accept))
                .build());
        // aussi dans l'onglet des mega-gemmes de Mega Showdown (si present)
        ItemGroupEvents.modifyEntriesEvent(MSD_MEGA_TAB).register(entries -> MEGA_STONES.forEach(entries::accept));

        // composants Mega Showdown poses par defaut sur chaque mega-gemme (apres l'init de tous les mods)
        DefaultItemComponentEvents.MODIFY.register(context -> {
            DataComponentType<String> type = component(MSD_TYPE);
            DataComponentType<ResourceLocation> location = component(MSD_LOCATION);
            if (type == null || location == null) {
                LOG.error("Mega Showdown introuvable : les mega-gemmes de Normandy Fakemons ne permettront pas de mega-evoluer");
                return;
            }
            for (MegaStoneItem stone : MEGA_STONES) {
                context.modify(stone, builder -> {
                    builder.set(type, "mega");
                    builder.set(location, stone.megaEntry());
                });
            }
        });

        ServerLifecycleEvents.SERVER_STARTED.register(NormandyFakemons::selfCheck);
        LOG.info("Normandy Fakemons : {} mega-gemme(s) enregistree(s)", MEGA_STONES.size());
    }

    private static MegaStoneItem registerMegaStone(String name, ResourceLocation megaEntry, String species) {
        MegaStoneItem item = Registry.register(BuiltInRegistries.ITEM, id(name),
                new MegaStoneItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant(), megaEntry, species));
        MEGA_STONES.add(item);
        return item;
    }

    @SuppressWarnings("unchecked")
    private static <T> DataComponentType<T> component(ResourceLocation key) {
        return (DataComponentType<T>) BuiltInRegistries.DATA_COMPONENT_TYPE.get(key);
    }

    /** Verification au demarrage du serveur : un resume dans les logs (detaille avec -Dnormandy_fakemons.selftest=true). */
    private static void selfCheck(MinecraftServer server) {
        boolean verbose = Boolean.getBoolean("normandy_fakemons.selftest");
        List<String> problems = new ArrayList<>();
        DataComponentType<String> type = component(MSD_TYPE);
        DataComponentType<ResourceLocation> location = component(MSD_LOCATION);
        ResourceKey<Registry<Object>> megaKey = ResourceKey.createRegistryKey(ResourceLocation.fromNamespaceAndPath("mega_showdown", "mega"));
        Optional<Registry<Object>> megaRegistry = server.registryAccess().registry(megaKey);
        for (MegaStoneItem stone : MEGA_STONES) {
            ItemStack stack = new ItemStack(stone);
            boolean ok = type != null && location != null && "mega".equals(stack.get(type)) && stone.megaEntry().equals(stack.get(location));
            if (!ok) problems.add(BuiltInRegistries.ITEM.getKey(stone) + " : composants Mega Showdown absents");
            if (megaRegistry.isEmpty() || !megaRegistry.get().containsKey(stone.megaEntry()))
                problems.add(stone.megaEntry() + " absent du registre mega_showdown:mega");
            if (verbose) LOG.info("SELFTEST item {} components={} mega_entry_loaded={}", BuiltInRegistries.ITEM.getKey(stone), ok,
                    megaRegistry.map(r -> r.containsKey(stone.megaEntry())).orElse(false));
        }
        boolean recipe = server.getRecipeManager().byKey(ResourceLocation.fromNamespaceAndPath("normandy", "deviljhonite")).isPresent();
        if (!recipe) problems.add("recette normandy:deviljhonite non chargee");
        int species = 0;
        for (String sid : SPECIES) {
            Object sp = cobblemonSpecies(sid);
            if (sp == null) problems.add("espece " + sid + " non chargee");
            else species++;
            if (verbose) LOG.info("SELFTEST species {} loaded={}", sid, sp != null);
        }
        if (verbose) LOG.info("SELFTEST recipe normandy:deviljhonite loaded={}", recipe);
        if (problems.isEmpty()) {
            LOG.info("Normandy Fakemons OK : {}/{} especes, {} mega-gemme(s), recette chargee", species, SPECIES.length, MEGA_STONES.size());
        } else {
            for (String p : problems) LOG.error("Normandy Fakemons : {}", p);
        }
        if (verbose) LOG.info("SELFTEST SUMMARY normandy_fakemons {} ({} probleme(s))", problems.isEmpty() ? "PASS" : "FAIL", problems.size());
    }

    static final String[] SPECIES = {"pomdraco", "arboverger", "cidrac", "drakflam", "vikinav", "drakkarthor", "meuhgousse",
            "bovecume", "normanguer", "etreroch", "archeolithe", "gargoylbatre", "rousselin", "roussinage", "homarbleu",
            "noroimard", "bolvados", "cruchevados", "alchibec", "archangelis", "sleipcheron", "guillopard", "deviljho"};

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
