package net.murphytalk.finance.window;

import com.vaadin.event.ShortcutAction;
import com.vaadin.server.ExternalResource;
import com.vaadin.server.Responsive;
import com.vaadin.server.ThemeResource;
import com.vaadin.shared.ui.BorderStyle;
import com.vaadin.ui.*;
import com.vaadin.ui.themes.ValoTheme;
import net.murphytalk.finance.dao.*;
import org.dussan.vaadin.dcharts.DCharts;
import org.dussan.vaadin.dcharts.data.DataSeries;
import org.dussan.vaadin.dcharts.metadata.renderers.SeriesRenderers;
import org.dussan.vaadin.dcharts.options.Highlighter;
import org.dussan.vaadin.dcharts.options.Legend;
import org.dussan.vaadin.dcharts.options.Options;
import org.dussan.vaadin.dcharts.options.SeriesDefaults;
import org.dussan.vaadin.dcharts.renderers.series.PieRenderer;

import java.util.Map;

public class InstrumentDetailsWindow extends Window {
    private final Instrument instrument;
    private final DAO dao;

    public InstrumentDetailsWindow(DAO dao, Instrument instrument) {
        this.dao = dao;
        this.instrument = instrument;
        //addStyleName("moviedetailswindow");
        Responsive.makeResponsive(this);

        setCaption(instrument.broker.fullName);
        setWidth(50, Unit.PERCENTAGE);
        setModal(true);
        setCloseShortcut(ShortcutAction.KeyCode.ESCAPE, null);
        setResizable(false);
        setClosable(false);

        VerticalLayout content = new VerticalLayout();
        content.setMargin(false);
        setContent(content);

        Panel detailsWrapper = new Panel(buildDetails());
        detailsWrapper.addStyleName(ValoTheme.PANEL_BORDERLESS);
        content.addComponent(detailsWrapper);

        content.addComponent(buildFooter());
    }

    @FunctionalInterface
    private interface AddDataSeriers{
        void add(DataSeries dataSeries);
    }

    private void addPieChartTab(TabSheet tabSheet, String caption, AddDataSeriers addDataSeriers){
        final VerticalLayout layout1 = new VerticalLayout();
        //layout1.setSizeFull();
        //layout1.setSpacing(true);
        //fields.addComponent(layout1);
        DataSeries dataSeries = new DataSeries().newSeries();
        addDataSeriers.add(dataSeries);
        SeriesDefaults seriesDefaults = new SeriesDefaults()
                .setRenderer(SeriesRenderers.PIE)
                .setRendererOptions(new PieRenderer().setShowDataLabels(true));

        Legend legend = new Legend().setShow(true);

        Highlighter highlighter = new Highlighter()
                .setShow(true)
                .setShowTooltip(true)
                .setTooltipAlwaysVisible(true)
                .setKeepTooltipInsideChart(true);

        Options options = new Options()
                .setSeriesDefaults(seriesDefaults)
                .setLegend(legend)
                .setHighlighter(highlighter);

        DCharts chart = new DCharts()
                .setDataSeries(dataSeries)
                .setOptions(options);
        layout1.addComponent(chart);
        layout1.setMargin(true);
        //layout1.setComponentAlignment(chart, Alignment.TOP_CENTER);
        layout1.setExpandRatio(chart, 1.f);
        chart.setSizeFull();
        //chart.setWidth(100, Unit.PERCENTAGE);
        chart.show();
        tabSheet.addTab(layout1, caption);
    }

    private Component buildDetails() {
        FormLayout fields = new FormLayout();
        fields.setSpacing(false);
        fields.setMargin(true);

        if(instrument.url!=null) {
            Link link = new Link(instrument.name, new ExternalResource(instrument.url));
            link.setTargetName("_blank");
            link.setTargetBorder(BorderStyle.DEFAULT);
            link.setTargetHeight(300);
            link.setTargetWidth(400);
            fields.addComponent(link);
        }
        else {
            fields.addComponent(new Label(instrument.name));
        }

        TabSheet tabs = new TabSheet();
        //tabs.setSizeFull();
        fields.addComponent(tabs);

        addPieChartTab(tabs,"Asset Allocation",(DataSeries d) -> {
            for (Map.Entry<Asset, Integer> e : dao.loadAssetAllocation(instrument).entrySet()) {
                d.newSeries().add(e.getKey().type, e.getValue());
            }
        });

        addPieChartTab(tabs,"Region Allocation",(DataSeries d) -> {
            for (Map.Entry<Asset, Integer> e : dao.loadAssetAllocation(instrument).entrySet()) {
                d.newSeries().add(e.getKey().type, e.getValue());
            }
        });


        //fixme : by default the chart in the first tab does not expand ...
        tabs.setSelectedTab(1);
        tabs.setSelectedTab(0);


        return fields;
    }

    private Component buildFooter() {
        HorizontalLayout footer = new HorizontalLayout();
        footer.setSpacing(true);

        footer.addStyleName(ValoTheme.WINDOW_BOTTOM_TOOLBAR);
        footer.setWidth(100.0f, Unit.PERCENTAGE);

        Label icon = new Label();
        icon.setIcon(new ThemeResource("Japan-Flag.png"));
        icon.setSizeUndefined();
        footer.addComponent(icon);


        Button ok = new Button("Close", this::cancel);
        ok.addStyleName(ValoTheme.BUTTON_PRIMARY);
        ok.focus();
        footer.addComponent(ok);
        footer.setComponentAlignment(ok, Alignment.TOP_RIGHT);
        return footer;
    }

    public void cancel(Button.ClickEvent event) {
        close();
    }

    public static void open(DAO dao, Instrument instrument) {
        Window w = new InstrumentDetailsWindow(dao, instrument);
        UI.getCurrent().addWindow(w);
        w.focus();
    }
}
