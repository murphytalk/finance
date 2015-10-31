package net.murphytalk.finance.dao;

import com.vaadin.spring.annotation.SpringComponent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.sql.DataSource;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
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
    static final Map<Integer,Asset>  assets  = new HashMap<>();
    static final Map<Integer,Broker> brokers = new HashMap<>();
    static final Map<Integer,Instrument> instruments = new HashMap<>();

    static private final String selectFromPerformanceByDate = "select * from performance where date>=%d and date<=%d";

    public static class StaticData {
        public int rowid;
        public void setRowid(int rowid) {
            this.rowid = rowid;
        }
    }

    public void loadStaticData(){
        for(Asset a:jdbcTemplate.query("select rowid,[type] from asset", new BeanPropertyRowMapper<>(Asset.class))){
            assets.put(a.rowid,a);
        }

        for(Broker b:jdbcTemplate.query("select rowid,[name] from broker", new BeanPropertyRowMapper<>(Broker.class))){
            brokers.put(b.rowid,b);
        }

        for(Instrument i:jdbcTemplate.query("select rowid,[name],asset,broker,currency from instrument", new BeanPropertyRowMapper<>(Instrument.class))){
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

    @Autowired
    public void setDataSource(DataSource dataSource){
        jdbcTemplate = new JdbcTemplate(dataSource);
        loadStaticData();
    }

}
