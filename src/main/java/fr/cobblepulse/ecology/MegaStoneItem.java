package fr.cobblepulse.ecology;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Mega-gemme : un objet simple a tenir ; Mega Showdown la reconnait grace a ses composants par defaut. */
public class MegaStoneItem extends Item {
    private final ResourceLocation megaEntry;
    private final String species;

    public MegaStoneItem(Properties properties, ResourceLocation megaEntry, String species) {
        super(properties);
        this.megaEntry = megaEntry;
        this.species = species;
    }

    public ResourceLocation megaEntry() {
        return megaEntry;
    }

    public String species() {
        return species;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        String key = getDescriptionId();
        tooltip.add(Component.translatable(key + ".lore").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable(key + ".lore2").withStyle(ChatFormatting.DARK_RED));
    }
}
