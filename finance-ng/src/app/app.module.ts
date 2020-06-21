import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { BrowserModule, HammerModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
// tslint:disable-next-line: max-line-length
import { IgxNavigationDrawerModule, IgxNavbarModule, IgxLayoutModule, IgxRippleModule, IgxGridModule } from '@infragistics/igniteui-angular';

import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { StocksGridComponent } from './stocksgrid/stocksgrid.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    StocksGridComponent
  ],
  imports: [
    FormsModule,
    BrowserModule,
    HammerModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    IgxNavigationDrawerModule,
    IgxNavbarModule,
    IgxLayoutModule,
    IgxRippleModule,
    IgxGridModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
