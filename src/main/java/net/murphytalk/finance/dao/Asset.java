package net.murphytalk.finance.dao;

import java.util.HashMap;
import java.util.Map;

/**
 * Created by Mu Lu (murphytalk@gmail) on 11/1/15.
 */
public enum Asset{
    Stock(0),
    GovernmentBond(1),
    CorpBond(2),
    REIT(3),
    Commodity(4),
    Cash(5),
    Max(6);

    private Asset(final int v){
        value = v;
    }

    public int getValue() {
        return value;
    }

    private final int value;

    private static final Map<Integer,Asset> _lookup = new HashMap<>();
    static{
        _lookup.put(Stock.getValue(),Stock);
        _lookup.put(GovernmentBond.getValue(),GovernmentBond);
        _lookup.put(CorpBond.getValue(),CorpBond);
        _lookup.put(REIT.getValue(),REIT);
        _lookup.put(Commodity.getValue(),Commodity);
        _lookup.put(Cash.getValue(),Cash);
    }

    public static Asset int2asset(Integer i){
        return _lookup.get(i);
    }
}
