package net.murphytalk.finance.window;

import com.vaadin.data.util.ObjectProperty;
import com.vaadin.event.ShortcutAction;
import com.vaadin.server.Responsive;
import com.vaadin.ui.*;
import com.vaadin.ui.themes.ValoTheme;
import net.murphytalk.finance.dao.*;

import java.util.Map;

public class EditInstrument extends Window {
    private final Instrument instrument;
    private final ComboBox currency = new ComboBox("Currency"); //todo: how does ComboBox data binding work?
    private final DAO dao;
    //private final IndexedContainer currency = new IndexedContainer();

    private AssetAllocation assetAllocation;
    //private OptionGroup currency;


    public EditInstrument(DAO dao, Instrument instrument) {
        this.dao = dao;
        this.instrument = instrument;
        addStyleName("moviedetailswindow");
        Responsive.makeResponsive(this);

        setCaption(instrument.name);
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

        for (Map.Entry<String, Currency> e : dao.currenciesByName.entrySet()) {
            currency.addItem(e.getKey());
        }
        currency.select(instrument.currency.name);
        fields.addComponent(currency);

        TabSheet tabs = new TabSheet();
        fields.addComponent(tabs);

        final VerticalLayout layout1 = new VerticalLayout();
        assetAllocation = dao.loadAssetAllocation(instrument);
        final TextField[] assetAllocations = new TextField[Asset.Max.getValue()];
        for (int i = 0; i < Asset.Max.getValue(); ++i) {
            final Asset a = Asset.int2asset(i);
            assetAllocations[i] = new TextField(a.name(), new ObjectProperty<>(assetAllocation.getAllocation(i)));
            layout1.addComponent(assetAllocations[i]);
        }
        tabs.addTab(layout1, "Asset Allocation");


        return fields;
    }

    private Component buildFooter() {
        HorizontalLayout footer = new HorizontalLayout();
        footer.setSpacing(true);

        footer.addStyleName(ValoTheme.WINDOW_BOTTOM_TOOLBAR);
        footer.setWidth(100.0f, Unit.PERCENTAGE);

        Button save = new Button("Save", this::save);
        //save.addStyleName(ValoTheme.BUTTON_PRIMARY);
        save.setClickShortcut(ShortcutAction.KeyCode.ENTER);
        footer.addComponent(save);

        Button ok = new Button("Close", this::cancel);
        ok.addStyleName(ValoTheme.BUTTON_PRIMARY);
        ok.focus();
        footer.addComponent(ok);
        footer.setComponentAlignment(ok, Alignment.TOP_RIGHT);
        return footer;
    }

    public void save(Button.ClickEvent event) {
        dao.saveInstrumentCurrency((String) currency.getValue());
        close();
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
