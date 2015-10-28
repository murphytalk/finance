package net.murphytalk.finance.dao;

import com.vaadin.spring.annotation.SpringComponent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.sql.DataSource;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by Mu Lu on 10/28/15.
 */
@SpringComponent
@Scope("singleton")
public class DAO {
    private JdbcTemplate jdbcTemplate;
    static final Map<Integer,Asset>  assets  = new HashMap<>();
    static final Map<Integer,Broker> brokers = new HashMap<>();
    static final Map<Integer,Instrument> instruments = new HashMap<>();

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

    public List<Performance> loadPerformance(LocalDate date){
        return jdbcTemplate.query("select * from performance",
                new BeanPropertyRowMapper<>(Performance.class));
    }

    @Autowired
    public void setDataSource(DataSource dataSource){
        jdbcTemplate = new JdbcTemplate(dataSource);
        loadStaticData();

        List<Performance> performances = loadPerformance(null);
    }

}
