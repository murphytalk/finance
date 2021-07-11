import { FundsPositionComponent } from './components/funds-position/funds-position.component';
import { FlaskAdminComponent } from './components/flask-admin/flask-admin.component';
import { StocksPositionComponent } from './components/stocks-position/stocks-position.component';
import { NgModule, Component } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { FinOverviewComponent } from './components/fin-overview/fin-overview.component';
import { FlaskApiComponent } from './components/flask-api/flask-api.component';

export const routes: Routes = [
  { path: 'overview', component: FinOverviewComponent , data: { text: 'Overview', icon: 'calculate' }},
  { path: 'stock', component: StocksPositionComponent, data: { text: 'Stocks Position', icon: 'dynamic_feed' }},
  { path: 'funds', component: FundsPositionComponent, data: { text: 'Funds Position', icon: 'dynamic_feed' }},
  { path: 'admin', component: FlaskAdminComponent, data: { text: 'Admin', icon: 'grading' }},
  { path: 'api', component: FlaskApiComponent, data: { text: 'API Doc', icon: 'help_center' }},
  { path: '', redirectTo: '/overview', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { relativeLinkResolution: 'legacy' })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
