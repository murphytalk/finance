package net.murphytalk.finance.dao;

/**
 * Created by Mu Lu (murphytalk@gmail) on 11/1/15.
 */
public class AssetAllocation {
    /*
      indexed by asset value -1
      e.g. allocation[0] is the percentage of stock asset
           allocation[5] is the percentage of cash asset
     */
    private Integer[] allocation = new Integer[Asset.Max.getValue()];

    public AssetAllocation() {
        for (int i = 0; i < Asset.Max.getValue(); ++i) {
            allocation[i] = new Integer(0);
        }
    }

    public void setAllocation(int asset, int ratio) {
        if (asset >= 0 && asset < Asset.Max.getValue()) {
            allocation[asset] = ratio;
        }
    }

    public Integer getAllocation(int asset) {
        return allocation[asset];
    }
}
