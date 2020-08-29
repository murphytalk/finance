import { Component, OnInit, ViewChild } from '@angular/core';
import { Router, RouterEvent, NavigationStart } from '@angular/router';
import { routes } from './app-routing.module';
import { filter } from 'rxjs/operators';
import { NGXLogger } from 'ngx-logger';
import { MatSidenav } from '@angular/material/sidenav';
@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
    topNavLinks: Array<{
        path: string;
        name: string;
        icon: string;
    }> = [];

    @ViewChild(MatSidenav, { static: true })
    private nav: MatSidenav;

    activePage: string;

    constructor(private router: Router, private logger: NGXLogger) {
        for (const route of routes) {
            if (route.path && route.data && route.path.indexOf('*') === -1) {
                this.topNavLinks.push({
                    name: route.data.text,
                    icon: route.data.icon,
                    path: '/' + route.path,
                });
            }

            this.router.events
                .pipe(filter((e) => e instanceof NavigationStart))
                .subscribe(
                    e => {
                        logger.log(e);
                        this.nav.close();
                    },
                    err => this.logger.error(err),
                    () => this.logger.info('nav sub done'));
        }
        this.activePage = this.topNavLinks[0].name;
    }

    ngOnInit(): void {}
}
