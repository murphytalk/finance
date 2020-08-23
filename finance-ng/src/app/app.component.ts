import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { routes } from './app-routing.module';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit{
  topNavLinks: Array<{
    path: string,
    name: string
  }> = [];

  activePage: string;

  constructor(private router: Router){
    for (const route of routes) {
      if (route.path && route.data && route.path.indexOf('*') === -1) {
        this.topNavLinks.push({
          name: route.data.text,
          path: '/' + route.path
        });
      }
    }
    this.activePage = this.topNavLinks[0].name;
  }

  ngOnInit(): void {
  }
}
