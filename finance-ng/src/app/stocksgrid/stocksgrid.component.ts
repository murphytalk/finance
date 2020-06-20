import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { employeesData } from './localData';
import { IgxColumnComponent } from '@infragistics/igniteui-angular';

@Component({
  selector: 'app-stocksgrid',
  templateUrl: './stocksgrid.component.html',
  styleUrls: ['./stocksgrid.component.scss']
})
export class StocksGridComponent implements OnInit {
  public localData: any[];
  title = 'stocksGrid';
  constructor() { }

  ngOnInit() {
    this.localData = employeesData;
  }

  public onColumnInit(column: IgxColumnComponent) {
    if (column.field === 'RegistererDate') {
      column.formatter = (date => date.toLocaleDateString());
    }
  }
}
