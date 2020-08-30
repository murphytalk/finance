import { FlaskAdminComponent } from './components/flask-admin/flask-admin.component';
import { StocksPositionComponent } from './components/stocks-position/stocks-position.component';
import { NgModule, Component } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { FinOverviewComponent } from './components/fin-overview/fin-overview.component';

export const routes: Routes = [
  { path: 'overview', component: FinOverviewComponent , data: { text: 'Overview', icon: 'calculate' }},
  { path: 'stock', component: StocksPositionComponent, data: { text: 'Stocks Position', icon: 'dynamic_feed' }},
  { path: 'admin', component: FlaskAdminComponent, data: { text: 'Admin', icon: 'grading' }},
  { path: '', redirectTo: '/overview', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
