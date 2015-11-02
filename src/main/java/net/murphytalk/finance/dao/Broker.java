package net.murphytalk.finance.dao;

/**
 * Created by Mu Lu (murphytalk@gmail.com) on 10/28/15.
 */
public class Broker extends DAO.StaticData {
    public String name;
    public String fullName;
    public void setName(String name) {
        this.name = name;
    }
    public void setFullName(String fullName) {
        this.fullName = fullName;
    }
}
