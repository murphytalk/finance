package net.murphytalk.finance.dao;

import com.vaadin.spring.annotation.SpringComponent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;

import javax.sql.DataSource;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by Mu Lu on 10/28/15.
 */
@SpringComponent
@Scope("singleton")
public class DAO {
    public static final ZoneOffset TIMEZONE = ZoneOffset.ofHours(9);
    private JdbcTemplate jdbcTemplate;
    static public final Map<Integer,InstrumentType> instrumentTypes = new HashMap<>();
    static public final Map<Integer,Currency> currencies = new HashMap<>();
    static public final Map<Integer,Broker> brokers = new HashMap<>();
    static public final Map<Integer,Instrument> instruments = new HashMap<>();

    static private final String selectFromPerformanceByDate = "select * from performance where date>=%d and date<=%d";

    public static class StaticData {
        public int rowid;
        public void setRowid(int rowid) {
            this.rowid = rowid;
        }
    }

    public void loadStaticData(){
        for(InstrumentType t:jdbcTemplate.query("select rowid,[type] from instrument_type", new BeanPropertyRowMapper<>(InstrumentType.class))){
            instrumentTypes.put(t.rowid, t);
        }

        for(Broker b:jdbcTemplate.query("select rowid,[name] from broker", new BeanPropertyRowMapper<>(Broker.class))){
            brokers.put(b.rowid,b);
        }

        for(Currency c:jdbcTemplate.query("select rowid,[name] from currency", new BeanPropertyRowMapper<>(Currency.class))){
            currencies.put(c.rowid,c);
        }

        for(Instrument i:jdbcTemplate.query("select rowid,[name],type,broker,currency from instrument", new BeanPropertyRowMapper<>(Instrument.class))){
            instruments.put(i.rowid,i);
        }
    }

    public List<Performance> loadPerformance(Date input){
        long epoch = input.getTime()/1000 ;//- TIMEZONE.getTotalSeconds();
        return jdbcTemplate.query(String.format(selectFromPerformanceByDate,epoch,epoch+24*3600),
                new BeanPropertyRowMapper<>(Performance.class));
    }

    public LocalDate getLatestPerformanceDate(){
        long epoch = jdbcTemplate.queryForLong("SELECT max(date) as date from performance");
        return LocalDateTime.ofEpochSecond(epoch, 0, DAO.TIMEZONE).toLocalDate();
    }

    public AssetAllocation loadAssetAllocation(Instrument instrument){
        final AssetAllocation result = new AssetAllocation();
        jdbcTemplate.query(String.format("select asset,ratio from asset_allocation where instrument = %d", instrument.rowid),
                rs -> {
                    result.setAllocation(rs.getInt(0),rs.getInt(1));
                });
        return result;
    }

    @Autowired
    public void setDataSource(DataSource dataSource){
        jdbcTemplate = new JdbcTemplate(dataSource);
        loadStaticData();
    }

}
