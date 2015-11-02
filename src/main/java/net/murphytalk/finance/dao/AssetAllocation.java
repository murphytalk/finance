package net.murphytalk.finance.dao;

import com.vaadin.data.util.ObjectProperty;
import com.vaadin.data.util.PropertysetItem;

/**
 * Created by Mu Lu (murphytalk@gmail) on 11/1/15.
 */
public class AssetAllocation {
    private PropertysetItem item = new PropertysetItem();

    public AssetAllocation() {
        for (int i = 0; i < Asset.Max.getValue(); ++i) {
            item.addItemProperty(Asset.int2asset(i).name(),new ObjectProperty<>(0));
        }
    }

    public void setAllocation(int asset, int ratio) {
        if (asset >= 0 && asset < Asset.Max.getValue()) {
            item.addItemProperty(Asset.int2asset(asset).name(),new ObjectProperty<>(ratio));
        }
    }

    public PropertysetItem getItem() {
        return item;
    }
}
