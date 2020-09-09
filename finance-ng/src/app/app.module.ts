import { FormatMoneyPipe } from './shared/pipes';
import { AgGridModule } from 'ag-grid-angular';
import { environment } from './../environments/environment';
import { FinOverviewComponent } from './components/fin-overview/fin-overview.component';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import {MatSidenavModule} from '@angular/material/sidenav';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatListModule} from '@angular/material/list';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button';
import {MatRadioModule} from '@angular/material/radio';
import {MatTabsModule} from '@angular/material/tabs';

import { NgxEchartsModule } from 'ngx-echarts';

import * as echarts from './shared/echarts';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { LoggerModule, NgxLoggerLevel } from 'ngx-logger';
import { StocksPositionComponent } from './components/stocks-position/stocks-position.component';
import { FlaskAdminComponent } from './components/flask-admin/flask-admin.component';
import { FlaskApiComponent } from './components/flask-api/flask-api.component';


@NgModule({
  declarations: [
    AppComponent,
    FormatMoneyPipe,
    FinOverviewComponent,
    StocksPositionComponent,
    FlaskAdminComponent,
    FlaskApiComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    LoggerModule.forRoot({
      serverLoggingUrl: '/api/logs',
      level: environment.logLevel,
      serverLogLevel: NgxLoggerLevel.OFF,
      disableConsoleLogging: false
    }),
    NgxEchartsModule.forRoot({
      echarts
    }),
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatRadioModule,
    MatTabsModule,
    AgGridModule.withComponents([]),
    NgbModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
