package net.murphytalk.finance.window;

import com.vaadin.event.ShortcutAction;
import com.vaadin.server.Responsive;
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

public class EditInstrument extends Window {
    private final Instrument instrument;
    private final DAO dao;

    public EditInstrument(DAO dao, Instrument instrument) {
        this.dao = dao;
        this.instrument = instrument;
        addStyleName("moviedetailswindow");
        Responsive.makeResponsive(this);

        setCaption(instrument.broker.name);
        setWidth(30, Unit.PERCENTAGE);
        setModal(true);
        setCloseShortcut(ShortcutAction.KeyCode.ESCAPE, null);
        setResizable(false);
        setClosable(false);

        VerticalLayout content = new VerticalLayout();
        content.setMargin(true);
        setContent(content);

        Panel detailsWrapper = new Panel(buildDetails());
        detailsWrapper.addStyleName(ValoTheme.PANEL_BORDERLESS);
        content.addComponent(detailsWrapper);

        content.addComponent(buildFooter());
    }

    private Component buildDetails() {
        FormLayout fields = new FormLayout();
        fields.setSpacing(false);
        fields.setMargin(true);

        fields.addComponent(new Label(instrument.name));
        fields.addComponent(new Label(instrument.currency.name));

        TabSheet tabs = new TabSheet();
        fields.addComponent(tabs);

        final VerticalLayout layout1 = new VerticalLayout();
        layout1.setSizeFull();
        layout1.setSpacing(true);

        DataSeries dataSeries = new DataSeries().newSeries();
        for(Map.Entry<Asset,Integer> e : dao.loadAssetAllocation(instrument).entrySet()){
            dataSeries.add(e.getKey().type,e.getValue());
        }
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
        layout1.setComponentAlignment(chart, Alignment.TOP_CENTER);
        chart.setSizeFull();
        chart.show();
        tabs.addTab(layout1, "Asset Allocation");



        return fields;
    }

    private Component buildFooter() {
        HorizontalLayout footer = new HorizontalLayout();
        footer.setSpacing(true);

        footer.addStyleName(ValoTheme.WINDOW_BOTTOM_TOOLBAR);
        footer.setWidth(100.0f, Unit.PERCENTAGE);

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
        Window w = new EditInstrument(dao, instrument);
        UI.getCurrent().addWindow(w);
        w.focus();
    }
}
