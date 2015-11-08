package net.murphytalk.finance.view;

import com.vaadin.data.util.BeanItem;
import com.vaadin.data.util.BeanItemContainer;
import com.vaadin.navigator.View;
import com.vaadin.navigator.ViewChangeListener;
import com.vaadin.server.Responsive;
import com.vaadin.ui.*;
import com.vaadin.ui.renderers.ClickableRenderer;
import com.vaadin.ui.themes.ValoTheme;
import net.murphytalk.finance.dao.DAO;
import net.murphytalk.finance.dao.Performance;
import net.murphytalk.finance.window.InstrumentDetailsWindow;
import org.vaadin.gridutil.renderer.ViewButtonValueRenderer;

import java.text.DecimalFormat;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;

/**
 * Created by Mu Lu (murphytalk@gmail) on 10/31/15.
 */
public final class Portfolio extends VerticalLayout implements View {
    private final Grid grid;
    private PopupDateField datePicker;
    private final DAO dao;
    private final DecimalFormat formatter = new DecimalFormat("#,###.00");

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

        List<Performance> performances = dao.loadPerformance(datePicker.getValue());

        float totalCapital = 0, totalValue = 0, totalProfit = 0;
        for(Performance p:performances){
            totalCapital+=p.capital;
            totalValue+=p.value;
            totalProfit+=p.profit;
        }


        bic.addAll(performances);
        final Grid g = new Grid(bic);
        //grid.setContainerDataSource(bic);  //this causes a NPE

        g.removeColumn("date");
        g.setColumnOrder("instrument", "price", "amount", "capital", "value","profit");

        //fixme: the eye icon rending is above the row in a way that is blocking the row to get mouse click event correctly
        g.getColumn("instrument").setRenderer(new ViewButtonValueRenderer(e -> {
            BeanItem<Performance> i = (BeanItem<Performance>) grid.getContainerDataSource().getItem(e.getItemId());
            InstrumentDetailsWindow.open(dao, i.getBean().instrument);
        }));


        initFooterRow(g,totalCapital,totalValue,totalProfit);
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
        datePicker.setDateFormat("yyyy-MM-dd");
        datePicker.addValueChangeListener(e -> updateData(datePicker.getValue()));

        header.addComponent(datePicker);

        return header;
    }

    private void initFooterRow(final Grid g,float totalCapital,float totalValue, float totalProfit){
        final Grid.FooterRow footerRow = g.appendFooterRow();
        footerRow.getCell("instrument").setHtml("<b>Total</b>");
        //footerRow.join("capital", "value","profit");
        footerRow.getCell("capital").setHtml("<b>"+formatter.format(totalCapital)+"</b>");
        footerRow.getCell("value").setHtml("<b>"+formatter.format(totalValue)+"</b>");
        footerRow.getCell("profit").setHtml("<b>"+formatter.format(totalProfit)+"</b>");
    }

    @Override
    public void enter(ViewChangeListener.ViewChangeEvent event) {
    }
}
