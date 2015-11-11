package net.murphytalk.finance.dao;

/**
 * Created by Mu Lu (murphytalk@gmail.com) on 10/28/15.
 */
public class Instrument extends DAO.StaticData {
    public String name;
    public InstrumentType type;
    public Broker broker;
    public Currency currency;
    public String url;

    public void setName(String name) {
        this.name = name;
    }

    public void setType(int type) {
        this.type = DAO.instrumentTypes.get(type);
    }

    public void setBroker(int broker) {
        this.broker = DAO.brokers.get(broker);
    }

    public void setCurrency(int currency) {
        this.currency = DAO.currencies.get(currency);
    }

    public void setUrl(String url) {
        this.url = url;
    }
}
