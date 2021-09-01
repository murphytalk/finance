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


import { LoggerModule, NgxLoggerLevel } from 'ngx-logger';
import { StocksPositionComponent } from './components/stocks-position/stocks-position.component';
import { FlaskAdminComponent } from './components/flask-admin/flask-admin.component';
import { FlaskApiComponent } from './components/flask-api/flask-api.component';
import { FundsPositionComponent } from './components/funds-position/funds-position.component';

// https://github.com/xieziyu/ngx-echarts#treeshaking-custom-build
// Import the echarts core module, which provides the necessary interfaces for using echarts.
import * as echarts from 'echarts/core';
// Import bar charts, all with Chart suffix
import { PieChart} from 'echarts/charts';
import { TitleComponent, TooltipComponent } from 'echarts/components';
// Import the Canvas renderer, note that introducing the CanvasRenderer or SVGRenderer is a required step
import { CanvasRenderer } from 'echarts/renderers';
import 'echarts/theme/macarons.js';
echarts.use([TitleComponent, TooltipComponent,  PieChart, CanvasRenderer]);

@NgModule({
  declarations: [
    AppComponent,
    FormatMoneyPipe,
    FinOverviewComponent,
    StocksPositionComponent,
    FlaskAdminComponent,
    FlaskApiComponent,
    FundsPositionComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    NgxEchartsModule.forRoot({ echarts }),
    LoggerModule.forRoot({
      serverLoggingUrl: '/api/logs',
      level: environment.logLevel,
      serverLogLevel: NgxLoggerLevel.OFF,
      disableConsoleLogging: false
    }),

    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatRadioModule,
    MatTabsModule,
    AgGridModule.withComponents([]),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
