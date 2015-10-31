package net.murphytalk.finance.dao;

import java.time.LocalDateTime;
import java.time.ZoneOffset;

/**
 * Created by Mu Lu (murphytalk@gmail.com) on 10/28/15.
 *
 * setters are used by Spring JdbcTemplate's BeanPropertyRowMapper
 * getters are used by Vaadin's BeanItemContainer
 */
public class Performance {
    private Instrument instrument;
    private int amount;
    private float price;
    private float value;
    private float profit;
    private float capital;
    private LocalDateTime date;

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
        this.date = LocalDateTime.ofEpochSecond(epoch,0,DAO.TIMEZONE);
    }

    public String getInstrument() {
        return instrument.name;
    }

    public int getAmount() {
        return amount;
    }

    public float getPrice() {
        return price;
    }

    public float getValue() {
        return value;
    }

    public float getProfit() {
        return profit;
    }

    public float getCapital() {
        return capital;
    }

    public String getDate() {
        return date.toString();
    }
}
