package net.murphytalk.finance;

import javax.servlet.annotation.WebListener;
import javax.servlet.annotation.WebServlet;

import com.vaadin.annotations.Theme;
import com.vaadin.annotations.Title;
import com.vaadin.server.VaadinRequest;
import com.vaadin.spring.annotation.EnableVaadin;
import com.vaadin.spring.annotation.SpringUI;
import com.vaadin.spring.server.SpringVaadinServlet;
import com.vaadin.ui.Layout;
import com.vaadin.ui.UI;
import net.murphytalk.finance.dao.DAO;
import net.murphytalk.finance.view.Portfolio;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.context.ContextLoaderListener;

@Theme("mytheme")
@Title("My Finance")
@SpringUI
public class MainUI extends UI {
    @Autowired
    private DAO dao;

    @Override
    protected void init(VaadinRequest vaadinRequest) {
        Layout layout = new Portfolio(dao);
        setContent(layout);
    }

    @Configuration
    @EnableVaadin
    public static class MyConfiguration {
    }

    @WebServlet(urlPatterns = "/*", asyncSupported = true)
    public static class MyUIServlet extends SpringVaadinServlet {
    }

    //http://stackoverflow.com/questions/11815339/role-purpose-of-contextloaderlistener-in-spring
    @WebListener
    public static class MyContextLoaderListener extends ContextLoaderListener {
    }
}
