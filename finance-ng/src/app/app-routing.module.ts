import { StocksPositionComponent } from './components/stocks-position/stocks-position.component';
import { NgModule, Component } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { FinOverviewComponent } from './components/fin-overview/fin-overview.component';

export const routes: Routes = [
  { path: 'overview', component: FinOverviewComponent , data: { text: 'Overview' }},
  { path: 'stock', component: StocksPositionComponent, data: { text: 'Stocks Position' }},
  { path: '', redirectTo: '/overview', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
