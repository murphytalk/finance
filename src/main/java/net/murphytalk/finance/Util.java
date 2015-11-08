package net.murphytalk.finance;

import com.vaadin.server.Resource;
import com.vaadin.server.ThemeResource;

/**
 * Created by Mu Lu (murphytalk@gmail) on 11/8/15.
 */
public class Util {
    private final static ThemeResource JPY = new ThemeResource("Japan-Flag.png");
    private final static ThemeResource USD = new ThemeResource("USA-Flag.png");

    public static final Resource getCurrencyIcon(String currency){
        switch(currency.toUpperCase()){
            case "JPY":
                return JPY;
            case "USD":
                return USD;
            default:
                return null;
        }
    }
}
