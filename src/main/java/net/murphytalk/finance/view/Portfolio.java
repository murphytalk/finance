package net.murphytalk.finance.view;

import com.vaadin.data.util.BeanItem;
import com.vaadin.data.util.BeanItemContainer;
import com.vaadin.navigator.View;
import com.vaadin.navigator.ViewChangeListener;
import com.vaadin.server.Responsive;
import com.vaadin.ui.*;
import com.vaadin.ui.themes.ValoTheme;
import net.murphytalk.finance.dao.DAO;
import net.murphytalk.finance.dao.Performance;
import net.murphytalk.finance.window.InstrumentDetailsWindow;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;

/**
 * Created by Mu Lu (murphytalk@gmail) on 10/31/15.
 */
public final class Portfolio extends VerticalLayout implements View {
    private final Grid grid;
    private PopupDateField datePicker;
    private final DAO dao;

    public Portfolio(DAO dao) {
        this.dao = dao;

        setSizeFull();
        addComponent(buildToolbar());

        grid = buildGrid();
        addComponent(grid);
        grid.setSizeFull();
        setExpandRatio(grid, 1);
    }

    private Grid buildGrid() {
        BeanItemContainer<Performance> bic = new BeanItemContainer<>(Performance.class);
        bic.addAll(dao.loadPerformance(datePicker.getValue()));
        final Grid g = new Grid(bic);
        //grid.setContainerDataSource(bic);  //this cause a NPE

        g.removeColumn("date");
        g.setColumnOrder("instrument", "price", "amount", "capital", "value");

        g.addItemClickListener(e ->
                {
                    if (e.isDoubleClick()) {
                        BeanItem<Performance> i = (BeanItem) e.getItem();
                        InstrumentDetailsWindow.open(dao, i.getBean().instrument);
                    }
                }
        );

        return g;
    }

    private void updateData(Date date) {
        BeanItemContainer<Performance> ds = (BeanItemContainer<Performance>) grid.getContainerDataSource();
        ds.removeAllItems();
        ds.addAll(dao.loadPerformance(date));
    }

    private Component buildToolbar() {
        HorizontalLayout header = new HorizontalLayout();
        header.addStyleName("viewheader"); //to align to right
        header.setSpacing(true);
        Responsive.makeResponsive(header);

        Label title = new Label("Portfolio");
        title.setSizeUndefined();
        title.addStyleName(ValoTheme.LABEL_H1);
        //title.addStyleName(ValoTheme.LABEL_NO_MARGIN);
        header.addComponent(title);

        LocalDate ld = dao.getLatestPerformanceDate();
        Instant instant = ld.atStartOfDay().atZone(ZoneId.systemDefault()).toInstant();
        datePicker = new PopupDateField("Performance Date", Date.from(instant));

        datePicker.addValueChangeListener(e -> updateData(datePicker.getValue()));

        header.addComponent(datePicker);

        return header;
    }


    @Override
    public void enter(ViewChangeListener.ViewChangeEvent event) {
    }
}
