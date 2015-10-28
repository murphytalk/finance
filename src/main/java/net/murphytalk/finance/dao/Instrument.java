package net.murphytalk.finance.dao;

/**
 * Created by Mu Lu (murphytalk@gmail.com) on 10/28/15.
 */
public class Instrument extends DAO.StaticData {
    public String name;
    public Asset asset;
    public Broker broker;
    public String currency;

    public void setName(String name) {
        this.name = name;
    }

    public void setAsset(int asset) {
        this.asset = DAO.assets.get(asset);
    }

    public void setBroker(int broker) {
        this.broker = DAO.brokers.get(broker);
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }
}
