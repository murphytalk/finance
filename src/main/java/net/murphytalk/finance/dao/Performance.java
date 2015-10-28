package net.murphytalk.finance.dao;

import java.time.LocalDateTime;
import java.time.ZoneOffset;

/**
 * Created by Mu Lu (murphytalk@gmail.com) on 10/28/15.
 */
public class Performance {
    public Instrument instrument;
    public int amount;
    public float price;
    public float value;
    public float profit;
    public float capital;
    public LocalDateTime date;

    public void setInstrument(int instrument) {
        this.instrument = DAO.instruments.get(instrument);
    }

    public void setAmount(int amount) {
        this.amount = amount;
    }

    public void setPrice(float price) {
        this.price = price;
    }

    public void setValue(float value) {
        this.value = value;
    }

    public void setProfit(float profit) {
        this.profit = profit;
    }

    public void setCapital(float capital) {
        this.capital = capital;
    }

    public void setDate(long epoch) {
        this.date = LocalDateTime.ofEpochSecond(epoch,0, ZoneOffset.ofHours(9));
    }
}
